"""The GA4 archive's bookkeeping: which tables are due, gaps, staleness, and never losing an archived file.

The BigQuery reads and Parquet writes need google-cloud-bigquery and pyarrow, which the dev group does not install
(the job gets them from the script's inline metadata), so these tests drive the pure functions and the archive step
with a fake writer. All data here is synthetic.
"""

import datetime
import json

import pytest

from scripts import analytics_archive as aa

TODAY = datetime.date(2026, 10, 29)
GA = aa.GA_DATASET


def info(rows, modified="2026-10-28T06:00:00+00:00"):
    return {"rows": rows, "modified": modified}


def test_table_day():
    assert aa.table_day("events_20261027") == datetime.date(2026, 10, 27)
    assert aa.table_day("events_intraday_20261029") is None
    assert aa.table_day("pseudonymous_users_20261027") is None
    assert aa.table_day("events_2026102") is None


def test_due_waits_for_the_settle_window():
    tables = {f"{GA}.events_202610{d}": info(5) for d in (25, 26, 27)}
    due = aa.due_tables(tables, {}, TODAY)
    # GA4 can still add late events to a day for 72 hours, so 10-27 is not settled on 10-29.
    assert due == [f"{GA}.events_20261025", f"{GA}.events_20261026"]


def test_due_skips_unsettled_tables_in_the_ga_dataset_but_not_other_datasets():
    tables = {f"{GA}.events_intraday_20261029": info(1), "ua_history.monthly_snapshots": info(24)}
    assert aa.due_tables(tables, {}, TODAY) == ["ua_history.monthly_snapshots"]


def test_due_when_bigquery_changed_since_archiving():
    ref = f"{GA}.events_20261020"
    manifest = {"tables": {ref: {**info(20), "file": "ga4/events_20261020.parquet"}}}
    assert aa.due_tables({ref: info(20)}, manifest, TODAY) == []
    assert aa.due_tables({ref: info(21)}, manifest, TODAY) == [ref]
    assert aa.due_tables({ref: info(20, "2026-10-29T01:00:00+00:00")}, manifest, TODAY) == [ref]


def test_missing_days():
    days = [datetime.date(2026, 10, d) for d in (13, 14, 16, 18, 19)]
    assert aa.missing_days(days) == ["2026-10-15", "2026-10-17"]
    assert aa.missing_days([]) == []


def test_stale_export():
    assert not aa.export_stale(datetime.date(2026, 10, 27), TODAY)
    assert aa.export_stale(datetime.date(2026, 10, 20), TODAY)
    assert aa.export_stale(None, TODAY)


def test_vanished_tables():
    manifest = {"tables": {f"{GA}.events_20261006": {}, f"{GA}.events_20261007": {}}}
    assert aa.vanished({f"{GA}.events_20261007": info(1)}, manifest) == [f"{GA}.events_20261006"]


def fake_writer(content):
    def write(client, ref, path):
        path.write_bytes(content)
        return len(content)

    return write


def test_archive_one_writes_and_records(tmp_path):
    ref = f"{GA}.events_20261020"
    manifest = {"tables": {}}
    aa.archive_one(None, ref, info(3), tmp_path, manifest, write=fake_writer(b"abc"), stamp="20261029T090000Z")
    entry = manifest["tables"][ref]
    assert entry["file"] == "ga4/events_20261020.parquet"
    assert (tmp_path / entry["file"]).read_bytes() == b"abc"
    assert entry["rows"] == 3 and entry["bytes"] == 3 and entry["superseded"] == []
    assert not list(tmp_path.rglob("*.tmp"))


def test_archive_one_rejects_a_row_count_mismatch(tmp_path):
    manifest = {"tables": {}}
    with pytest.raises(aa.ArchiveError, match="2 rows"):
        aa.archive_one(None, f"{GA}.events_20261020", info(3), tmp_path, manifest, write=fake_writer(b"ab"), stamp="s")
    assert manifest["tables"] == {}
    assert not list((tmp_path / "ga4").iterdir())


def test_archive_one_keeps_the_superseded_file(tmp_path):
    ref = f"{GA}.events_20261020"
    manifest = {"tables": {}}
    aa.archive_one(None, ref, info(3), tmp_path, manifest, write=fake_writer(b"old"), stamp="20261023T090000Z")
    aa.archive_one(None, ref, info(4), tmp_path, manifest, write=fake_writer(b"newx"), stamp="20261029T090000Z")
    entry = manifest["tables"][ref]
    assert (tmp_path / entry["file"]).read_bytes() == b"newx"
    [old] = entry["superseded"]
    assert old["file"] == "ga4/superseded/events_20261020.20261023T090000Z.parquet"
    assert (tmp_path / old["file"]).read_bytes() == b"old"
    assert old["rows"] == 3


def test_one_failing_table_does_not_block_the_rest(tmp_path):
    bad, good = f"{GA}.events_20261020", f"{GA}.events_20261021"

    def write(client, ref, path):
        path.write_bytes(b"partial")
        if ref == bad:
            raise aa.ArchiveError("type did not survive the round trip")
        path.write_bytes(b"ok")
        return 2

    manifest = {"tables": {}}
    failed = aa.archive_due(None, [bad, good], {bad: info(2), good: info(2)}, tmp_path, manifest, "s", write=write)
    assert failed == [bad]
    assert list(manifest["tables"]) == [good]
    assert sorted(p.name for p in (tmp_path / "ga4").iterdir()) == ["events_20261021.parquet"]
    assert (tmp_path / "manifest.json").exists()


def test_manifest_round_trip(tmp_path):
    assert aa.load_manifest(tmp_path) == {"tables": {}}
    aa.save_manifest(tmp_path, {"tables": {"a.b": {"rows": 1}}})
    assert json.loads((tmp_path / "manifest.json").read_text())["tables"]["a.b"]["rows"] == 1
    assert not list(tmp_path.glob("*.tmp"))

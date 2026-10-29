# /// script
# requires-python = ">=3.12"
# dependencies = ["google-cloud-bigquery>=3.25", "pyarrow>=17"]
# ///
"""Archive every day of the site's GA4 BigQuery export to Google Drive, so the analytics are never lost.

The GA4 export (stharrold-github-io.analytics_393124094, one events_YYYYMMDD table per day with any traffic) keeps
data for as long as billing stays on and nobody deletes the dataset; GA4 cannot backfill a day it failed to export.
This job keeps a second copy: each settled day (SETTLE_DAYS old, because GA4 still adds late events for 72 hours)
becomes ga4/events_YYYYMMDD.parquet under ARCHIVE_DIR, is read back and compared with BigQuery, and is recorded in
manifest.json with its row count, BigQuery's last-modified time and a sha256. A table that changes in BigQuery later
is archived again and the old file kept under ga4/superseded/; nothing is ever deleted. Tables in the other
datasets (ua_history: the Universal Analytics history recovered from emails) are archived the same way.

Run by launchd from a copy outside ~/Documents (scripts/install_analytics_launchd.sh), through
scripts/analytics_archive.sh. By hand, from the repository root:

    uv run --script scripts/analytics_archive.py --dry-run   # what is due, change nothing
    uv run --script scripts/analytics_archive.py

Auth is the gmail.com account's gcloud login (a short-lived token from `gcloud auth print-access-token`), never the
application-default credentials, which belong to another account. The rows include visitor pseudonymous IDs and
locations: the archive stays in the private Drive folder and never goes in git.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT = "stharrold-github-io"
ACCOUNT = "samuel.harrold@gmail.com"
GA_DATASET = "analytics_393124094"
# Dataset -> folder in the archive.
DATASETS = {GA_DATASET: "ga4", "ua_history": "ua_history"}
ARCHIVE_DIR = Path(os.environ.get("ARCHIVE_DIR", "~/Library/CloudStorage/GoogleDrive-samuel.harrold@gmail.com/My Drive/My_Drive/Data/stharrold.github.io")).expanduser()
SETTLE_DAYS = 3  # GA4 updates a day's table for up to 72 hours
STALE_DAYS = 7  # quiet days have no table at all (3-6 events on a normal day), so a short threshold would cry wolf
DAY_RE = re.compile(r"^events_(\d{8})$")
REPO_URL = "https://github.com/stharrold/stharrold.github.io"


def version() -> str:
    """The commit this script came from: the installed copy's VERSION file, else the repository's HEAD."""
    here = Path(__file__).resolve().parent
    stamp = here.parent / "VERSION"
    if stamp.exists():
        return stamp.read_text().strip()
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=here)
    return r.stdout.strip() or "src_develop"


def readme(commit: str) -> str:
    """README.md for the archive folder, so whoever finds the files can find the process that made them."""
    src = f"{REPO_URL}/blob/{commit}"
    return f"""# stharrold.github.io analytics archive

Private copy of the Google Analytics 4 BigQuery export for https://stharrold.github.io, kept so the site's analytics
are never lost. Written by `scripts/analytics_archive.py` in {REPO_URL}; this file is rewritten on every run.

- Made by: [{commit[:7]}]({src}/scripts/analytics_archive.py), the code of the latest run; each table in `manifest.json`
  records the `commit` that wrote it (entries without one are from the first run, 2026-10-29, by a draft of the
  code first committed in 49e9f65). How it works and how to install it: [README, "Analytics archive"]({src}/README.md).
- Source: BigQuery project `{PROJECT}`, datasets {", ".join(f"`{d}`" for d in DATASETS)}.
- Schedule: a launchd job on the author's Mac, 09:00 and 21:00 (`bash scripts/install_analytics_launchd.sh`), running a
  copy in `~/Library/Application Support/stharrold-analytics/`; log in `~/Library/Logs/stharrold-analytics.log`.

## Files

- `ga4/events_YYYYMMDD.parquet`: one GA4 export day, archived once it is {SETTLE_DAYS} days old (GA4 adds late
  events for 72 hours). Schema: [GA4 BigQuery export](https://support.google.com/analytics/answer/7029846).
- `ua_history/monthly_snapshots.parquet`: Universal Analytics monthly totals, 2017-11 to 2019-10, recovered from GA
  snapshot emails.
- `*/superseded/<table>.<stamp>.parquet`: an earlier archive of a table that later changed in BigQuery. Nothing is
  deleted.
- `manifest.json`: per table, the file, row count, BigQuery last-modified time, bytes, sha256, archive stamp and commit;
  `missing_days` (no export table: no visitors, or a failed export); `last_run`.

## Read

```
uv run --with duckdb python -c "import duckdb; print(duckdb.sql(\\"select event_date, count(*) from 'ga4/*.parquet' group by 1 order by 1\\"))"
```

Rerun by hand from a clone: `uv run --script scripts/analytics_archive.py` (`--dry-run` lists what is due).

The rows include pseudonymous browser IDs and approximate locations: keep this folder private and out of git.
"""


class ArchiveError(Exception):
    pass


def table_day(table_id: str) -> datetime.date | None:
    """The date of a daily export table (events_YYYYMMDD); None for intraday and every other table."""
    m = DAY_RE.match(table_id)
    return datetime.datetime.strptime(m.group(1), "%Y%m%d").date() if m else None


def due_tables(tables: dict, manifest: dict, today: datetime.date) -> list[str]:
    """Tables to archive now: settled, and new or changed since archived.

    `tables` maps "dataset.table" to {"rows", "modified"} from BigQuery. In the GA dataset only settled daily tables
    count; other datasets are archived whole.
    """
    archived = manifest.get("tables", {})
    due = []
    for ref, meta in sorted(tables.items()):
        dataset, table_id = ref.split(".", 1)
        if dataset == GA_DATASET:
            day = table_day(table_id)
            if day is None or day > today - datetime.timedelta(days=SETTLE_DAYS):
                continue
        old = archived.get(ref)
        if old is None or (old["rows"], old["modified"]) != (meta["rows"], meta["modified"]):
            due.append(ref)
    return due


def missing_days(days: list[datetime.date]) -> list[str]:
    """Days between the first and last daily table that have no table: no visitors, or a failed export."""
    if not days:
        return []
    have, out = set(days), []
    d = min(days)
    while d < max(days):
        if d not in have:
            out.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return out


def export_stale(newest: datetime.date | None, today: datetime.date) -> bool:
    return newest is None or (today - newest).days > STALE_DAYS


def vanished(tables: dict, manifest: dict) -> list[str]:
    """Archived tables no longer in BigQuery: the archive is now their only copy."""
    return sorted(set(manifest.get("tables", {})) - set(tables))


def load_manifest(root: Path) -> dict:
    path = root / "manifest.json"
    return json.loads(path.read_text()) if path.exists() else {"tables": {}}


def save_manifest(root: Path, manifest: dict) -> None:
    """Write through a temporary file and rename, so a crash never leaves a half-written manifest."""
    tmp = root / "manifest.json.tmp"
    tmp.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, root / "manifest.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_parquet(client, ref: str, path: Path) -> int:
    """Copy a BigQuery table to Parquet, read the file back, and return its row count.

    list_rows reads through tabledata.list, which BigQuery does not bill. Parquet keeps the export's nested and
    repeated fields (event_params and the rest) that CSV cannot hold.
    """
    import pyarrow.parquet as pq

    table = client.list_rows(f"{PROJECT}.{ref}").to_arrow(create_bqstorage_client=False)
    pq.write_table(table, path, compression="zstd")
    back = pq.read_table(path)
    if not back.equals(table):
        raise ArchiveError(f"{ref}: the Parquet file read back differs from what BigQuery returned")
    return back.num_rows


def archive_one(client, ref: str, meta: dict, root: Path, manifest: dict, write=write_parquet, stamp: str = "", commit: str = "") -> dict:
    """Archive one table and record it; an earlier archive of it is moved to superseded/, never deleted."""
    dataset, table_id = ref.split(".", 1)
    folder = root / DATASETS[dataset]
    folder.mkdir(exist_ok=True)
    final = folder / f"{table_id}.parquet"
    tmp = folder / f"{table_id}.parquet.tmp"
    try:
        rows = write(client, ref, tmp)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    if rows != meta["rows"]:
        tmp.unlink()
        raise ArchiveError(f"{ref}: wrote {rows} rows, BigQuery reports {meta['rows']}")
    entry = {
        "file": str(final.relative_to(root)),
        "rows": rows,
        "modified": meta["modified"],
        "bytes": tmp.stat().st_size,
        "sha256": sha256(tmp),
        "stamp": stamp,
        "commit": commit,
        "superseded": [],
    }
    old = manifest["tables"].get(ref)
    if old is not None and final.exists():
        (folder / "superseded").mkdir(exist_ok=True)
        kept = folder / "superseded" / f"{table_id}.{old['stamp']}.parquet"
        os.replace(final, kept)
        entry["superseded"] = old.get("superseded", []) + [{k: v for k, v in old.items() if k != "superseded"} | {"file": str(kept.relative_to(root))}]
    os.replace(tmp, final)
    manifest["tables"][ref] = entry
    return entry


def archive_due(client, due: list[str], tables: dict, root: Path, manifest: dict, stamp: str, write=write_parquet, commit: str = "") -> list[str]:
    """Archive each due table, saving the manifest after each; return the ones that failed.

    One table that keeps failing must not block the days after it, so a failure is logged and the loop goes on.
    """
    failed = []
    for ref in due:
        try:
            entry = archive_one(client, ref, tables[ref], root, manifest, write=write, stamp=stamp, commit=commit)
        except Exception as e:
            print(f"[FAIL] {ref}: {type(e).__name__}: {e}")
            failed.append(ref)
            continue
        save_manifest(root, manifest)
        print(f"[OK] {ref}: {entry['rows']} rows -> {entry['file']}" + (" (earlier copy kept in superseded/)" if entry["superseded"] else ""))
    return failed


def gcloud(*args: str) -> str:
    r = subprocess.run(["gcloud", *args, f"--account={ACCOUNT}"], capture_output=True, text=True)
    if r.returncode:
        raise ArchiveError(f"gcloud {args[0]} {args[1]}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f'exit {r.returncode}'}")
    return r.stdout.strip()


def bigquery_client():
    from google.cloud import bigquery
    from google.oauth2.credentials import Credentials

    return bigquery.Client(project=PROJECT, credentials=Credentials(token=gcloud("auth", "print-access-token")))


def list_tables(client) -> dict:
    tables = {}
    for dataset in DATASETS:
        for item in client.list_tables(f"{PROJECT}.{dataset}"):
            t = client.get_table(item.reference)
            tables[f"{dataset}.{t.table_id}"] = {"rows": t.num_rows, "modified": t.modified.isoformat()}
    return tables


def notify(title: str, message: str) -> None:
    subprocess.run(["osascript", "-e", f"display notification {json.dumps(message)} with title {json.dumps(title)}"], capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="report what is due; write nothing")
    args = parser.parse_args()
    now = datetime.datetime.now(datetime.UTC)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    today = datetime.date.today()
    # Never create the archive root: if Drive is not running, a fresh local folder here would sync nowhere.
    if not ARCHIVE_DIR.is_dir():
        raise ArchiveError(f"archive folder not found: {ARCHIVE_DIR} (is Google Drive running?)")

    client = bigquery_client()
    tables = list_tables(client)
    manifest = load_manifest(ARCHIVE_DIR)
    due = due_tables(tables, manifest, today)
    days = sorted(d for ref in tables if ref.startswith(GA_DATASET + ".") and (d := table_day(ref.split(".", 1)[1])))
    warnings = []
    if export_stale(days[-1] if days else None, today):
        warnings.append(f"newest GA4 export table is {days[-1] if days else 'missing'}: the export may have stopped")
    if gone := vanished(tables, manifest):
        warnings.append(f"{len(gone)} archived tables are no longer in BigQuery (the archive is the only copy): {', '.join(gone)}")
    if gcloud("billing", "projects", "describe", PROJECT, "--format=value(billingEnabled)") != "True":
        warnings.append(f"billing is off for {PROJECT}: the export stops, and new tables may expire")

    print(f"[INFO] {stamp} {len(tables)} tables in BigQuery, {len(manifest['tables'])} archived, {len(due)} due: {', '.join(due) or 'none'}")
    if args.dry_run:
        for w in warnings:
            print(f"[WARN] {w}")
        return 0

    commit = version()
    failed = archive_due(client, due, tables, ARCHIVE_DIR, manifest, stamp, commit=commit)
    (ARCHIVE_DIR / "README.md").write_text(readme(commit))
    manifest["generated_by"] = {"script": f"{REPO_URL}/blob/{commit}/scripts/analytics_archive.py", "commit": commit}
    manifest["missing_days"] = missing_days(days)
    manifest["last_run"] = {"stamp": stamp, "archived": [r for r in due if r not in failed], "failed": failed, "warnings": warnings}
    save_manifest(ARCHIVE_DIR, manifest)

    for w in warnings:
        print(f"[WARN] {w}")
    if failed:
        raise ArchiveError(f"{len(failed)} of {len(due)} tables failed ({', '.join(failed)}); the rest were archived")
    if warnings:
        notify("Site analytics archive: check needed", warnings[0])
    elif due:
        notify("Site analytics archived", f"{len(due)} tables copied to Drive and verified")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[FAIL] {datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H:%M:%SZ} {type(e).__name__}: {e}")
        notify("Site analytics archive failed", f"{type(e).__name__}: {e}"[:200])
        sys.exit(1)

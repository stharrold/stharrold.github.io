"""The readership report's SQL and bookkeeping, on synthetic GA4-shaped Parquet (no real visitors, no network)."""

import datetime

import duckdb
import pytest

from scripts import analytics_report as ar

NOW = datetime.datetime(2026, 11, 5, 12, tzinfo=datetime.UTC)


def event(day, name, visitor, page, **params):
    """One GA4 export row in the shape of the BigQuery schema (only the fields the report reads)."""
    params = {"page_location": f"https://stharrold.github.io{page}?utm=x", **params}
    kv = ", ".join(
        f"{{'key': '{k}', 'value': {{'string_value': {repr(v) if isinstance(v, str) else 'NULL'}, 'int_value': {v if isinstance(v, int) else 'NULL'}}}}}"
        for k, v in params.items()
    )
    return f"('{day}', '{name}', '{visitor}', [{kv}], {{'source': 'google', 'medium': 'organic'}}, {{'country': 'United States'}})"


@pytest.fixture
def ga4(tmp_path):
    rows = [
        # A reader: views the post, engages, scrolls to 90%, opens the notebook.
        event("20261028", "page_view", "a", "/20261027-post.html", session_engaged="1"),
        event("20261028", "user_engagement", "a", "/20261027-post.html", engagement_time_msec=42000),
        event("20261028", "scroll", "a", "/20261027-post.html", percent_scrolled=90),
        event("20261028", "notebook_open", "a", "/20261027-post.html", link_url="https://stharrold.github.io/x-full.html"),
        # A crawler: one home page view, no engagement.
        event("20261028", "page_view", "bot", "/"),
        # A reader eight days later, outside the first-7-days window.
        event("20261104", "page_view", "b", "/20261027-post.html", session_engaged="1"),
        event("20261104", "click", "b", "/20261027-post.html", outbound="true", link_url="https://osf.io/c53w9"),
    ]
    path = tmp_path / "events.parquet"
    duckdb.sql(
        "copy (select * from (values " + ", ".join(rows) + ") t(event_date, event_name, user_pseudo_id, event_params, traffic_source, geo)) to '" + str(path) + "'"
    )
    return ar.connect([str(path)])


def test_page_counts_separate_engaged_visitors_from_crawlers(ga4):
    cols, rows = ar.table(ga4, ar.PAGES_SQL)
    by_page = {r[0]: dict(zip(cols, r, strict=True)) for r in rows}
    post = by_page["/20261027-post.html"]
    assert post["views"] == 2 and post["visitors"] == 2 and post["engaged_visitors"] == 2
    assert post["engaged_seconds"] == 42.0 and post["read_to_90pct"] == 1
    assert post["notebook_opens"] == 1 and post["outbound_clicks"] == 1
    home = by_page["/"]
    assert home["visitors"] == 1 and home["engaged_visitors"] == 0


def test_post_windows(ga4):
    post = {"slug": "20261027-post", "title": "t", "date": datetime.date(2026, 10, 27), "tags": []}
    old = {"slug": "20160110-old", "title": "o", "date": datetime.date(2016, 1, 10), "tags": []}
    new, before = ar.post_windows(ga4, [post, old], datetime.date(2026, 10, 6))
    assert (new["first_7_days"], new["first_30_days"], new["all"]) == (1, 2, 2)
    assert before["first_7_days"] is None and before["first_30_days"] is None and before["all"] == 0


def test_health_flags_a_stale_or_failing_archive():
    good = {"tables": {"analytics_393124094.events_20261101": {}}, "last_run": {"stamp": "20261105T090000Z", "warnings": [], "failed": []}}
    h = ar.health(good, NOW)
    assert h["ok"] and h["hours_since"] == 3.0 and h["ga4_last"] == "2026-11-01"
    stale = good | {"last_run": {"stamp": "20261103T090000Z", "warnings": ["billing is off"], "failed": ["x"]}}
    assert ar.health(stale, NOW)["problems"] == ["billing is off", "failed: x", "the archive job last ran 51 hours ago"]
    assert not ar.health({"tables": {}}, NOW)["ok"]


def test_posts_reads_published_articles(tmp_path):
    (tmp_path / "a.md").write_text("Title: A\nDate: 2026-10-27T17:30:00Z\nSlug: a-slug\nTags: dbt, duckdb\n\nBody\n")
    (tmp_path / "b.md").write_text("Title: B\nDate: 2026-11-01\nStatus: draft\n\nBody\n")
    assert ar.posts(tmp_path) == [{"slug": "a-slug", "title": "A", "date": datetime.date(2026, 10, 27), "tags": ["dbt", "duckdb"]}]


def test_save_never_overwrites(tmp_path):
    day = datetime.date(2026, 11, 5)
    assert ar.save(tmp_path, "one", day).name == "2026-11-05.md"
    assert ar.save(tmp_path, "two", day).name == "2026-11-05-2.md"
    assert (tmp_path / "reports" / "2026-11-05.md").read_text() == "one"


def test_search_console_without_data(tmp_path):
    assert "No Search Console data" in ar.search_console(tmp_path)


def test_rank_note_uses_engaged_visitors():
    cols = ["page", "visitors", "engaged_visitors"]
    assert ar.rank_note(cols, [("/", 68, 11), ("/a.html", 12, 2)]).startswith("**Too little data")
    assert "the top page has 31" in ar.rank_note(cols, [("/", 5, 31)])
    assert ar.rank_note(cols, []).startswith("**Too little data")

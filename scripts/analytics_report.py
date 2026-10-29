# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.3", "google-cloud-bigquery>=3.25", "pyarrow>=17"]
# ///
"""Readership report for the /analytics skill: archive health, who reads which post, and how people find the site.

Every number the skill reports comes from here, computed with DuckDB over the analytics archive on Google Drive
(scripts/analytics_archive.py) plus the GA4 days still only in BigQuery (the archive waits 3 days before copying a
day; those are read for free with tabledata.list and never written anywhere). Run from the repository root:

    uv run --script scripts/analytics_report.py           # print the report
    uv run --script scripts/analytics_report.py --save    # also save it to <archive>/reports/YYYY-MM-DD.md

Traffic is small and much of it is crawlers (direct, one page, no engagement), so every count is given for all
visitors and for engaged visitors (GA4's session_engaged, or any engagement time), and pages are ranked only once
one has RANK_MIN engaged visitors. The report holds totals only, never visitor IDs.

Anyone can send events to a public GA4 tag, and search queries are typed by strangers, so page paths, sources and
queries are untrusted text that an agent will read. Pages outside the site's own paths are grouped as "(other)", and
every cell is reduced to a safe character set and length (cell()).
"""

import argparse
import datetime
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analytics_archive as aa  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RANK_MIN = 30  # engaged visitors a page needs before a ranking means anything
# The site's own page paths; anything else in page_location is grouped as "(other)" (see known_page()).
SITE_PAGE_RE = re.compile(r"^/((tag|category)/[a-z0-9-]+\.html|(archives|categories|tags|search)\.html)?$")
CELL_MAX = 80
FRESH_HOURS = 13  # the job runs at 09:00 and 21:00, so a healthy archive has run within 12 hours

MACROS = """
create or replace macro pstr(params, k) as list_filter(params, lambda p: p.key = k)[1].value.string_value;
create or replace macro pint(params, k) as list_filter(params, lambda p: p.key = k)[1].value.int_value;
create or replace macro page_path(url) as coalesce(nullif(regexp_extract(url, '^https?://[^/]+(/[^?#]*)', 1), ''), '/');
"""

# One row per event with the fields the report needs; `engaged` marks events in an engaged session.
EVENTS_SQL = """
create or replace view ev_raw as
select
    strptime(event_date, '%Y%m%d')::date as day,
    event_name,
    user_pseudo_id as visitor,
    page_path(pstr(event_params, 'page_location')) as page,
    coalesce(pstr(event_params, 'session_engaged') = '1', false) or coalesce(pint(event_params, 'engagement_time_msec'), 0) > 0 as engaged,
    coalesce(pint(event_params, 'engagement_time_msec'), 0) as engagement_ms,
    coalesce(pint(event_params, 'percent_scrolled'), 0) as percent_scrolled,
    coalesce(pstr(event_params, 'outbound'), '') = 'true' as outbound,
    traffic_source.source as source,
    traffic_source.medium as medium,
    geo.country as country
from read_parquet({files}, union_by_name = true);
create or replace view ev as select * from ev_raw
"""

PAGES_SQL = """
select
    page,
    count(*) filter (event_name = 'page_view') as views,
    count(distinct visitor) filter (event_name = 'page_view') as visitors,
    count(distinct visitor) filter (engaged) as engaged_visitors,
    round(sum(engagement_ms) / 1000.0, 1) as engaged_seconds,
    count(distinct visitor) filter (event_name = 'scroll' and percent_scrolled >= 90) as read_to_90pct,
    count(*) filter (event_name = 'notebook_open') as notebook_opens,
    count(*) filter (event_name = 'click' and outbound) as outbound_clicks
from ev
group by page
having views > 0
order by engaged_visitors desc, visitors desc, page
"""

SOURCES_SQL = """
select coalesce(source, '(none)') || ' / ' || coalesce(medium, '(none)') as source,
       count(distinct visitor) as visitors, count(distinct visitor) filter (engaged) as engaged_visitors
from ev group by 1 order by visitors desc limit 10
"""

COUNTRIES_SQL = """
select coalesce(nullif(country, ''), '(unknown)') as country,
       count(distinct visitor) as visitors, count(distinct visitor) filter (engaged) as engaged_visitors
from ev group by 1 order by visitors desc limit 10
"""

DAILY_SQL = """
select day, count(distinct visitor) as visitors, count(distinct visitor) filter (engaged) as engaged_visitors
from ev group by day order by day
"""


def metadata(path: Path) -> dict:
    """Pelican Markdown metadata: `Key: value` lines up to the first blank line, keys lowercased."""
    meta = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            break
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip().lower()] = value.strip()
    return meta


def posts(content: Path) -> list[dict]:
    """Published articles: slug, title, publish date and tags, newest first."""
    out = []
    for path in sorted(content.glob("*.md")):
        m = metadata(path)
        if m.get("status", "published").lower() != "published":
            continue
        out.append(
            {
                "slug": m.get("slug", path.stem),
                "title": m.get("title", path.stem),
                "date": datetime.date.fromisoformat(m["date"][:10]),
                "tags": [t.strip() for t in m.get("tags", "").split(",") if t.strip()],
            }
        )
    return sorted(out, key=lambda p: p["date"], reverse=True)


def cell(value) -> str:
    """A value as a Markdown table cell: no pipes, backticks, angle brackets or control characters, at most CELL_MAX."""
    if value is None:
        return ""
    text = re.sub(r"[\x00-\x1f\x7f|`<>\\]", " ", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= CELL_MAX else text[: CELL_MAX - 1] + "…"


def known_pages(content: Path) -> set[str]:
    """Paths the site actually serves for posts and pages (drafts and hidden pages included; they may be linked)."""
    paths = {f"/{metadata(p).get('slug', p.stem)}.html" for p in content.glob("*.md")}
    return paths | {f"/pages/{metadata(p).get('slug', p.stem)}.html" for p in (content / "pages").glob("*.md")}


def known_page(path: str, known: set[str]) -> str:
    return path if path in known or SITE_PAGE_RE.match(path) else "(other)"


def health(manifest: dict, now: datetime.datetime) -> dict:
    """Whether the archive job is keeping up: last run, its warnings and failures, and what is archived."""
    last = manifest.get("last_run", {})
    stamp = last.get("stamp")
    age = (now - datetime.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=datetime.UTC)).total_seconds() / 3600 if stamp else None
    days = sorted(d for ref in manifest.get("tables", {}) if ref.startswith(aa.GA_DATASET + ".") and (d := aa.ref_day(ref)))
    problems = list(last.get("warnings", [])) + [f"failed: {r}" for r in last.get("failed", [])]
    if age is None or age > FRESH_HOURS:
        problems.append(f"the archive job last ran {'never' if age is None else f'{age:.0f} hours ago'}")
    return {
        "last_run": stamp,
        "hours_since": None if age is None else round(age, 1),
        "archived_tables": len(manifest.get("tables", {})),
        "ga4_first": days[0].isoformat() if days else None,
        "ga4_last": days[-1].isoformat() if days else None,
        "missing_days": manifest.get("missing_days", []),
        "problems": problems,
        "ok": not problems,
    }


def rank_note(columns: list[str], rows: list[tuple]) -> str:
    """Whether the page table may be read as a ranking: only once the top page has RANK_MIN engaged visitors."""
    top = max((r[columns.index("engaged_visitors")] for r in rows), default=0)
    if top >= RANK_MIN:
        return f"Pages are ranked by engaged visitors (the top page has {top}; the order means something from {RANK_MIN})."
    return f"**Too little data to rank pages**: the most-engaged page has {top} engaged visitors (needs {RANK_MIN}). Read the table as counts, not a ranking."


def post_windows(con, post_list: list[dict], first_day: datetime.date) -> list[dict]:
    """Engaged visitors per post in its first 7 and 30 days, and in all the data; a window before the archive is None."""
    rows = []
    for p in post_list:
        page = f"/{p['slug']}.html"
        row = {"slug": p["slug"], "published": p["date"].isoformat()}
        for label, days in (("first_7_days", 7), ("first_30_days", 30)):
            if first_day is None or p["date"] < first_day:
                row[label] = None
                continue
            end = p["date"] + datetime.timedelta(days=days)
            row[label] = con.execute("select count(distinct visitor) from ev where page = ? and engaged and day >= ? and day < ?", [page, p["date"], end]).fetchone()[0]
        row["all"] = con.execute("select count(distinct visitor) from ev where page = ? and engaged", [page]).fetchone()[0]
        rows.append(row)
    return rows


def connect(files: list[str], known: set[str] | None = None):
    """Events as the view `ev`; with `known`, pages outside the site's own paths become "(other)"."""
    import duckdb

    con = duckdb.connect()
    con.execute(MACROS)
    con.execute(EVENTS_SQL.format(files=json.dumps(files).replace('"', "'")))
    if known is not None:
        # Same rule as known_page(), in SQL (a Python UDF would need numpy).
        con.execute("create temp table known_page (path varchar)")
        con.executemany("insert into known_page values (?)", [[k] for k in sorted(known)])
        con.execute(
            "create or replace view ev as select * replace (case when page in (select path from known_page) "
            f"or regexp_full_match(page, '{SITE_PAGE_RE.pattern}') then page else '(other)' end as page) from ev_raw"  # a constant, no quotes
        )
    return con


def table(con, sql: str) -> tuple[list[str], list[tuple]]:
    cur = con.execute(sql)
    return [c[0] for c in cur.description], cur.fetchall()


def markdown_table(columns: list[str], rows: list) -> str:
    out = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    out += ["| " + " | ".join(cell(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def recent_days(manifest: dict, folder: Path) -> list[str]:
    """GA4 days in BigQuery that the archive has not copied yet (the last 3 days), as Parquet files in `folder`."""
    import pyarrow.parquet as pq

    client = aa.bigquery_client()
    out = []
    for item in client.list_tables(f"{aa.PROJECT}.{aa.GA_DATASET}"):
        ref = f"{aa.GA_DATASET}.{item.table_id}"
        if aa.table_day(item.table_id) and ref not in manifest.get("tables", {}):
            path = folder / f"{item.table_id}.parquet"
            pq.write_table(client.list_rows(f"{aa.PROJECT}.{ref}").to_arrow(create_bqstorage_client=False), path)
            out.append(str(path))
    return out


def search_console(archive: Path) -> str:
    """Top queries and pages from the latest backfill and the bulk export, or a note that there is none yet."""
    import duckdb

    backfills = sorted((archive / "searchconsole_backfill").glob("*/web__date_query.parquet"))
    export = archive / "searchconsole" / "searchdata_url_impression"
    parts = []
    if export.is_dir() and any(export.glob("*.parquet")):
        # sum_position is zero-based (top result = 0), so the average position is sum_position / impressions + 1.
        parts.append(
            f"select data_date::date as day, query, impressions, clicks, sum_position + impressions as pos_x_imp "
            f"from read_parquet('{export}/*.parquet') where query is not null"
        )
    if backfills:
        cut = f"(select min(data_date)::date from read_parquet('{export}/*.parquet'))" if parts else "date '9999-12-31'"
        parts.append(
            f"select date::date as day, query, impressions, clicks, position * impressions as pos_x_imp from read_parquet('{backfills[-1]}') where date::date < {cut}"
        )
    if not parts:
        return "No Search Console data archived yet (bulk export from 2026-10-29; history pending the one-time backfill, issue #77)."
    sql = f"""
        select query, sum(impressions) impressions, sum(clicks) clicks, round(sum(pos_x_imp) / sum(impressions), 1) avg_position
        from ({" union all ".join(parts)}) group by query order by impressions desc limit 20
    """
    cur = duckdb.sql(sql)
    return markdown_table(cur.columns, cur.fetchall()) + "\n\nQueries Google judged rare are omitted from per-query rows (anonymized)."


def report(archive: Path, include_bigquery: bool = True, now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(datetime.UTC)
    manifest = aa.load_manifest(archive)
    h = health(manifest, now)
    files = [str(archive / e["file"]) for ref, e in sorted(manifest.get("tables", {}).items()) if ref.startswith(aa.GA_DATASET + ".")]
    with tempfile.TemporaryDirectory() as tmp:
        if include_bigquery:
            files += recent_days(manifest, Path(tmp))
        if not files:
            raise aa.ArchiveError(f"no GA4 data in {archive} or BigQuery")
        con = connect(files, known_pages(ROOT / "content"))
        first = con.execute("select min(day), max(day), count(distinct visitor), count(distinct visitor) filter (engaged) from ev").fetchone()
        pages = table(con, PAGES_SQL)
        windows = post_windows(con, posts(ROOT / "content"), first[0])
        sources, countries, daily = (table(con, q) for q in (SOURCES_SQL, COUNTRIES_SQL, DAILY_SQL))
    note = rank_note(*pages)
    lines = [
        f"# Site analytics report, {now:%Y-%m-%d %H:%M} UTC",
        "",
        f"Made by `scripts/analytics_report.py` at {aa.version()[:7]} ({aa.REPO_URL}). Totals only; no visitor IDs.",
        "",
        "## Archive health",
        "",
        f"- {'OK' if h['ok'] else 'NEEDS ATTENTION'}: last run {h['last_run']} ({h['hours_since']} h ago), "
        f"{h['archived_tables']} tables archived, GA4 {h['ga4_first']} to {h['ga4_last']}.",
        f"- Days with no GA4 table (no visitors, or a failed export): {', '.join(h['missing_days']) or 'none'}.",
        *[f"- Problem: {p}" for p in h["problems"]],
        "",
        "## Readership",
        "",
        f"Data {first[0]} to {first[1]}{' (last days read live from BigQuery)' if include_bigquery else ''}: {first[2]} visitors, {first[3]} engaged. {note}",
        "",
        markdown_table(*pages),
        "",
        "### Posts: engaged visitors after publishing",
        "",
        markdown_table(["slug", "published", "first_7_days", "first_30_days", "all"], [tuple(w.values()) for w in windows]),
        "",
        "A blank window predates the archive (it starts 2026-10-06).",
        "",
        "### Sources",
        "",
        markdown_table(*sources),
        "",
        "### Countries",
        "",
        markdown_table(*countries),
        "",
        "### Daily",
        "",
        markdown_table(*daily),
        "",
        "## Search Console",
        "",
        search_console(archive),
        "",
    ]
    return "\n".join(lines)


def save(archive: Path, text: str, today: datetime.date) -> Path:
    """Write reports/YYYY-MM-DD.md, adding -2, -3... rather than overwriting an earlier report from the same day."""
    folder = archive / "reports"
    folder.mkdir(exist_ok=True)
    path, n = folder / f"{today.isoformat()}.md", 1
    while path.exists():
        n += 1
        path = folder / f"{today.isoformat()}-{n}.md"
    path.write_text(text)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--save", action="store_true", help="also save the report to <archive>/reports/")
    parser.add_argument("--no-bigquery", action="store_true", help="use only the archive (no live read of the last days)")
    args = parser.parse_args()
    if not aa.ARCHIVE_DIR.is_dir():
        raise aa.ArchiveError(f"archive folder not found: {aa.ARCHIVE_DIR} (is Google Drive running?)")
    text = report(aa.ARCHIVE_DIR, include_bigquery=not args.no_bigquery)
    print(text)
    if args.save:
        print(f"[saved] {save(aa.ARCHIVE_DIR, text, datetime.date.today())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Build notes: the site's analytics archive and readership report (for a post about the blog, #27)

A running log of how the analytics pipeline was built: what it is for, what was checked, what went wrong and what
was changed. The code is `scripts/analytics_archive.py`, `scripts/analytics_report.py` and the `/analytics` skill
(`.claude/skills/analytics/SKILL.md`); README "Analytics archive" describes how to run it. Newest entries at the bottom.

## Goal (2026-10-29)

Never lose the site's analytics, and use them to decide what to write next. The model was an existing App Store
analytics job in another project: a scheduled pull, an archive copy with a count check, and a notification. That job
exists because Apple serves only about five weeks of daily data; here the risk was different.

## The risk, checked first (2026-10-29)

Read-only checks of the GA4 BigQuery export before building anything:
- billing is enabled on the project, so BigQuery's sandbox 60-day table expiry does not apply;
- neither the dataset nor its tables have an expiration;
- every daily table since the link (2026-10-06) is present, except two days with no events at all.

So nothing was expiring. The exposure was a single copy in one account, with nothing watching the export: GA4 cannot
backfill a day it failed to export.

## The archive (2026-10-29, 49e9f65, merged 9837792)

- A daily copy of each GA4 table to Parquet in a private Google Drive folder. Parquet keeps the export's nested
  `event_params`; tabledata.list reads the rows without BigQuery charges.
- A day is copied once it is 3 days old, because GA4 adds late events for 72 hours. Each file is read back and
  compared with BigQuery's row count, and a manifest records rows, last-modified time and a sha256. A table that
  changes later is copied again, with the old file kept; nothing is ever deleted.
- Warnings for a stale export (newest table over 7 days old; quiet days have no table, so a shorter threshold would
  cry wolf), a table leaving BigQuery, or billing turned off.
- A launchd job runs it twice a day from a copy outside `~/Documents`, which launchd cannot read.
- Tested first from a throwaway launchd job, because that could have changed the design. Under launchd, Python
  could write, rename and list in the Drive folder, but `/bin/ls` was refused there, so all file work stays in Python.
- A review caught that one persistently failing table would block every later day; failures are now per table.
- The first run copied 19 days and the Universal Analytics history; checksums, a DuckDB read of the nested fields, and
  a second run (nothing due) confirmed it.
- The privacy page now says the events are kept indefinitely (deployed d597f09).

## The archive explains itself (2026-10-29, 81b17f0)

The job writes a README into the Drive folder on every run, linking to the code at the exact commit that ran, and the
manifest records the writing commit per table, so anyone who finds the files can find the process.

## Search Console (2026-10-29, 1024a72)

- Search Console was added as a URL-prefix property, verified automatically through the GA4 tag, and linked to GA4.
- The GA4 link does not put Search Console data in the BigQuery export, and Search Console keeps only 16 months, so
  its separate bulk export to BigQuery was switched on as well. Its tables are partitioned by day, so the archive copies
  one partition per file rather than rewriting a growing table.
- The bulk export does not backfill, so the earlier history is saved once through the Search Console API, with a
  login kept in its own gcloud configuration so the default credentials are untouched. It waits on Search Console
  processing the new property (#77).

## The readership report and the `/analytics` skill (2026-10-29, ffb8f60)

- Every number comes from one script: DuckDB over the archive plus the newest days still only in BigQuery.
- Most traffic is crawlers (direct, one page, no engagement), so every count is given for all and for engaged
  visitors, and pages are ranked only once one has 30 engaged visitors. The first report correctly refused to rank:
  the most-engaged page had 11.
- A first draft of the ranking rule read the wrong column; extracting it into a tested function fixed it.

## Untrusted text (2026-10-29, 3b6664f)

A background security review pointed out that anyone can send events to a public GA4 tag, and search queries are
typed by strangers, so the report an agent reads could carry text written to steer it. Pages outside the site's own
paths are grouped as "(other)", every table cell is reduced to a safe character set and length, and the skill tells
the agent to treat those cells as data only.

## The owner's own visits (2026-10-29, c9118af)

With about 15 engaged visitors, the author's own visits mattered. Three measures:
- a GA4 internal-traffic rule for the home network, with the Internal Traffic filter set to Active (irreversible,
  and not retroactive);
- the Google Analytics opt-out add-on in the desktop browser (checked: the site loads and sends no collect request);
- a private list of the author's browser IDs (the `_ga` cookie value is GA4's `user_pseudo_id`), which the report
  drops from past data too.

The one engaged visit to the newest post turned out to be the author's phone, so after the exclusions the post had
no outside readers yet: the honest baseline for the next post.

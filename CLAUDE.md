# CLAUDE.md

Guidance for AI coding agents working in this repository. Read `README.md` first for commands and workflow.

## Rules

- **Stage explicit paths, never `git add -A`.** Untracked files appear here (e.g. `.playwright-mcp/` from browser
  automation, stray build artifacts) and a blanket add once pushed GA admin snapshots to the public repo.
- **Do not commit `output/`.** It is generated; CI builds and deploys it.
- **Verify before shipping:** `uv run ruff check . && uv run ruff format --check . && uv run pytest`. The tests build
  the publish site and encode past regressions (drafts, analytics tag, search index, comments, sitemap).
- **Deploys happen on push to `src_master`.** Merge feature branches into `src_develop`, then `src_develop` into
  `src_master` (`--no-ff`). Never push `src_master` with unreviewed visual changes.
- **Treat `master` as legacy.** It held `ghp-import` output until 2026-10-06; don't publish to it.

## Gotchas learned the hard way

- **GitHub Pages source must be "GitHub Actions".** In 2026 the setting had silently drifted to `src_master` at `/`,
  which would have published the raw source tree. Check with
  `gh api repos/stharrold/stharrold.github.io/pages --jq '{build_type, source}'`.
- **Drafts:** `Status: draft` posts are excluded by `DRAFT_SAVE_AS = ""` in `publishconf.py`, but their static files
  are not; add the draft's folder to `STATIC_EXCLUDES`.
- **`--autoreload` leaves orphans.** Killing only the parent `pelican` process leaves multiprocessing workers that keep
  rebuilding `output/` with dev settings. Stop it with Ctrl-C, or `pkill -f 'stharrold.github.io/.venv/bin/python -c from multiprocessing'`.
- **Pelican rewrites `PLUGINS`** to full module names (`pelican.plugins.tag_cloud`) after loading, so templates must
  not test `'name' in PLUGINS`; test the context variable instead (e.g. `{% if tag_cloud %}`).
- **Math needs block-level `$$...$$`.** `pymdownx.arithmatex` treats `$$...$$` inside a paragraph or after a hard line
  break as inline math. Put display equations in their own paragraph (indented inside list items).
- **Vendored CSS from Bootswatch** contains a Google Fonts `@import` whose URL has semicolons; strip it with
  `@import url([^)]*);`, not `[^;]*;`, or the following `:root` rule breaks.
- **Analytics:** GA4 is set only in `publishconf.py`; dev builds must not load it (tested). Avoid generating test
  page views on the live site; verify against a local dev build instead.
- **Privacy page:** when adding any third-party script or request, update `content/pages/privacy.md`.

## Layout

- `content/` posts and pages (Markdown); `content/static/<slug>/` notebooks, exports, images; `content/extra/` robots.txt, favicons.
- `themes/datasciencedemos/` Bootstrap 5 theme (see `themes/README.md` for lineage and vendored assets).
- `plugins/pelican_alias.py` local plugin for `Alias:` redirects.
- `data/archived-comments/` static HTML of 2016-2017 Disqus comments, loaded by `pelicanconf.py`.
- `tests/test_site.py` builds the site and checks the output.

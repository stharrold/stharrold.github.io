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
- **There is no `master` branch.** It held `ghp-import` output until 2026-10-06 and is archived as the tag
  `legacy-ghp-import-master`; don't recreate it or publish with `ghp-import`.
- **Pin GitHub Actions to commit SHAs** with the version in a comment (`uses: owner/action@<sha>  # vX.Y.Z`).
  Dependabot updates them. Keep jobs that write (issues, pages) separate from jobs that run third-party code.
- **Dependabot** version PRs target `src_develop`; security PRs target `src_master`, and merging one deploys.
- **Published 2015-2016 posts are frozen.** Never edit their text or fix their dead links. If a theme or rendering
  change needs a Markdown edit to an old post, ask first.
- **Open work lives in GitHub milestones** (one per post, plus "Site maintenance"): `gh issue list --milestone "<name>"`.
  The household-income demo plan is #68.

## Useful commands

- `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha` - resolve an action tag to a SHA for pinning (setup-uv has no major tags).
- `gh run list --workflow pages.yml --json databaseId,headSha` then `gh run watch <id>` - match runs by commit; the list lags a few seconds after a push.
- `curl -s "https://stharrold.github.io/<path>?v=$(date +%s)"` - cache-busted live check after a deploy.
- `uv run pelican -s pelicanconf.py -o <dir>` then `python3 -m http.server` in `<dir>` - stable preview for Playwright screenshots (not `--autoreload`).

## Gotchas learned the hard way

- **GitHub Pages source must be "GitHub Actions".** In 2026 the setting had silently drifted to `src_master` at `/`,
  which would have published the raw source tree. Check with
  `gh api repos/stharrold/stharrold.github.io/pages --jq '{build_type, source}'`.
- **Drafts:** `Status: draft` posts are excluded by `DRAFT_SAVE_AS = ""` in `publishconf.py`, but their static files
  are not; add the draft's folder to `STATIC_EXCLUDES`, and remove it when publishing (a test enforces both).
- **Keep tests content-driven.** Derive expectations from `content/` and `data/` (see `posts()`/`pages()` in
  `tests/test_site.py`); never hard-code slugs or counts, or publishing a post will block deploys.
- **Builds use `--fatal warnings`** in CI and tests, so any Pelican warning blocks a deploy; fix the warning.
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
- **Scheduled workflows stop after 60 quiet days** (GitHub disables them in public repos without activity). If the
  weekly link log has gone stale, run `gh workflow enable links.yml`.
- **Shell is zsh:** quote URLs containing `?` and globs like `--include='*.html'`; don't store a command in a variable
  (`$CMD args` doesn't word-split), use a function.
- **`articles` is narrowed on tag and category pages,** so site-wide template values (e.g. the copyright year) must
  come from settings, not from `articles`.
- **Live-site checks with Playwright:** block `googletagmanager.com|google-analytics.com` with `page.route` so
  verification adds no GA page views.
- **Pygments is capped `<2.20` by Pelican 4.12.** Dependabot can't fix capped transitive deps; alert #6 was dismissed
  as tolerable risk (see #64). Recheck when Pelican releases.
- **An interrupted tool call may already have run** (e.g. `gh workflow run`); check `gh run list` or the issue list
  before saying nothing happened.

## Layout

- `content/` posts and pages (Markdown); `content/static/<slug>/` notebooks, exports, images; `content/extra/` robots.txt, favicons.
- `themes/datasciencedemos/` Bootstrap 5 theme (see `themes/README.md` for lineage and vendored assets).
- `plugins/pelican_alias.py` local plugin for `Alias:` redirects.
- `data/archived-comments/` static HTML of 2016-2017 Disqus comments, loaded by `pelicanconf.py`.
- `tests/test_site.py` builds the site and checks the output.

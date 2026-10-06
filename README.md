# stharrold.github.io

Source for [Data Science Demos](https://stharrold.github.io), a blog built with [Pelican](https://getpelican.com/)
and deployed to GitHub Pages by GitHub Actions.

## Quick start

Requirements: [uv](https://docs.astral.sh/uv/) (Python 3.12+). All dependencies are pinned in `pyproject.toml` and `uv.lock`.

```bash
uv sync                                         # install Pelican, plugins, Pagefind, dev tools
uv run pre-commit install                       # once: ruff and file checks on commit
uv run pelican --settings pelicanconf.py        # build the dev site into output/ (drafts included, no analytics)
uv run python -m pagefind --site output         # build the search index (rerun after each build)
uv run pelican --listen                         # serve output/ at http://localhost:8000
uv run pytest                                   # build the publish site in a temp dir and check it
```

`uv run pelican --settings pelicanconf.py --autoreload --listen` rebuilds on every change, but each rebuild deletes
`output/pagefind/`, so search only works after rerunning Pagefind. Stop it with Ctrl-C; killing only the parent
process leaves its file watcher running.

## Branches and deployment

| Branch | Purpose |
|---|---|
| `src_master` | Production source. Every push builds, tests, and deploys the site (`.github/workflows/pages.yml`). |
| `src_develop` | Integration branch; pushes run the same checks without deploying. |
| `src_feature_*` | Feature branches off `src_develop` (git-flow); merged with `--no-ff`. |
| `master` | Legacy. Held the built site (via `ghp-import`) until 2026-10-06; no longer deployed. |

To release: merge `src_feature_*` into `src_develop`, then `src_develop` into `src_master`, and push. The workflow runs
ruff, pytest, `pelican --settings publishconf.py --fatal warnings`, and Pagefind, then deploys `output/`.
GitHub Pages must be set to **Settings > Pages > Source: GitHub Actions**. `output/` is generated and not tracked.

`pelicanconf.py` holds the site settings; `publishconf.py` extends it for production (absolute URLs, feeds, GA4,
no drafts).

## Writing posts

Posts are Markdown files in `content/` with a metadata header (`Title`, `Date`, `Modified`, `Category`, `Tags`,
`Slug`, `Summary`, optional `Related_posts` and `Alias` for old URLs). Pages go in `content/pages/`. Notebooks,
notebook HTML exports, and images go in `content/static/<slug>/` and are linked with `{static}/static/<slug>/...`.

- **Drafts:** `Status: draft` renders only in dev builds (`output/drafts/`). Static files are copied regardless of
  status, so add a draft's `static/<slug>` folder to `STATIC_EXCLUDES` in `publishconf.py`, and remove it when the
  post is published.
- **Math:** `$...$` inline and `$$...$$` display (as its own paragraph); rendered by MathJax 4.
  Prices such as `$20` are left alone.
- **Old posts:** posts last updated 5+ years before the build year show an "out of date" notice
  (`OUTDATED_AFTER_YEARS`).

## Site features

- **Theme:** `themes/datasciencedemos/`, Bootstrap 5 with Bootswatch Flatly, forked from pelican-bootstrap3;
  see `themes/README.md`.
- **Search:** [Pagefind](https://pagefind.app/), built from `output/` after Pelican; runs in the browser.
- **Comments:** [giscus](https://giscus.app/) (GitHub Discussions, Announcements category; requires the giscus
  GitHub App on this repository). Comments from Disqus (2016-2017) are archived as static HTML in
  `data/archived-comments/<slug>.html`.
- **Analytics:** Google Analytics 4 (`G-K4PX9089RZ`, publish builds only, Google signals off), exported daily to
  BigQuery project `stharrold-github-io` (dataset `analytics_393124094`). Universal Analytics history recovered from
  the GA monthly snapshot emails (2017-11 to 2019-10) is in `stharrold-github-io.ua_history.monthly_snapshots`.
- **Privacy:** `content/pages/privacy.md` lists every third-party service the site loads; update it when adding one.
- **Plugins:** `related_posts`, `tag_cloud`, `sitemap` (from PyPI), and `plugins/pelican_alias.py`
  (Python 3 port of [pelican-alias](https://github.com/Nitron/pelican-alias)) for `Alias:` redirects.

## License

Code: [MIT](LICENSE). Content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), except where indicated
otherwise. Vendored theme assets keep their own licenses (`themes/datasciencedemos/licenses/`).

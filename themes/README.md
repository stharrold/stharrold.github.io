# Themes

## datasciencedemos

The site theme: Bootstrap 5 with the [Bootswatch Flatly](https://bootswatch.com/flatly/) styles, no jQuery.

**Lineage.** Forked in 2026-10 from
[pelican-bootstrap3](https://github.com/getpelican/pelican-themes/tree/2b80541d755cd2d7891672650a52444e4d685e22/pelican-bootstrap3)
(MIT, see `licenses/pelican-bootstrap3-LICENSE.txt`), which the site used from 2015. The templates were rewritten
for Bootstrap 5 and trimmed to the features this site uses: article and page layouts, breadcrumbs, sidebar
(recent posts, categories, tag cloud), related posts, comments, GA4, and search. Removed: i18n/translations,
AddThis, Shariff, Twitter, Piwik/Matomo, series, GitHub widgets, liquid_tags, banners, Tipue Search, jQuery.

**Settings used by the templates** (see `pelicanconf.py`): `DISPLAY_PAGES_ON_MENU`, `DISPLAY_BREADCRUMBS`,
`DISPLAY_ARTICLE_INFO_ON_INDEX`, `DISPLAY_RECENT_POSTS_ON_SIDEBAR` / `RECENT_POST_COUNT`,
`DISPLAY_CATEGORIES_ON_SIDEBAR`, `DISPLAY_TAGS_ON_SIDEBAR` (needs the `tag_cloud` plugin), `SHOW_ARTICLE_CATEGORY`,
`SHOW_DATE_MODIFIED`, `FAVICON`, `TOUCHICON`, `PYGMENTS_STYLE`, `GOOGLE_ANALYTICS` / `GOOGLE_ANALYTICS_CONFIG` /
`GA_GTM_CONTAINER_ID`, `GISCUS` / `ARCHIVED_COMMENTS`, `BUILD_YEAR` / `OUTDATED_AFTER_YEARS` (notice on old posts),
`COPYRIGHT_START_YEAR` (footer shows start year through `BUILD_YEAR`), `FOOTER_LINKS`.

**Search.** `templates/search.html` uses the [Pagefind](https://pagefind.app/) Component UI. Post and page bodies
are marked `data-pagefind-body`; related posts, comments, and notices are `data-pagefind-ignore`. The index is built
after Pelican: `uv run python -m pagefind --site output`.

**Vendored assets** (update by replacing the files and the versions here). Dependabot does not track these or the
MathJax CDN pin in `templates/includes/math.html` (update its SRI hash too), so review them a few times a year:

| File | Source | License |
|---|---|---|
| `static/css/bootstrap.flatly.min.css` | bootswatch 5.3.8 `dist/flatly/bootstrap.min.css`, with its Google Fonts `@import` removed | MIT |
| `static/js/bootstrap.bundle.min.js` | bootstrap 5.3.8 `dist/js/bootstrap.bundle.min.js` | MIT |
| `static/fonts/lato-latin-*.woff2`, `static/css/lato.css` | @fontsource/lato 5.3.0 (self-hosted so pages make no Google Fonts request) | SIL OFL 1.1 |
| `static/css/font-awesome.min.css`, `static/fonts/fontawesome-webfont.*`, `FontAwesome.otf` | Font Awesome 4.7.0, from pelican-bootstrap3 | CSS MIT, fonts SIL OFL 1.1 |
| `static/css/pygments/default.css` | from pelican-bootstrap3 | MIT |

License texts are in `licenses/`.

# Vendored themes

`pelican-bootstrap3/` is copied from
[getpelican/pelican-themes](https://github.com/getpelican/pelican-themes/tree/2b80541d755cd2d7891672650a52444e4d685e22/pelican-bootstrap3)
at commit `2b80541d755cd2d7891672650a52444e4d685e22` (2025-10-22).

## Local patches

Pelican >= 4.5 rewrites `PLUGINS` to full module names (e.g. `pelican.plugins.tag_cloud`),
so the theme's `'<name>' in PLUGINS` checks never match namespace plugins. These checks
were changed to also accept the full name:

- `templates/base.html`: both `'tipue_search' in PLUGINS` checks (search CSS, navbar search box).
- `templates/includes/sidebar/tag_cloud.html`: `'tag_cloud' in PLUGINS` check.

Other fixes:

- `static/tipuesearch/tipuesearch.js`: added `escapeHtml()` and applied it where the search query
  is inserted as HTML (the "Showing results for" replace message and related-search button ids),
  fixing a reflected XSS via `search.html?q=`. `templates/search.html` now loads `tipuesearch.js`
  instead of the unpatched `tipuesearch.min.js`.
- `templates/includes/ga.html`: the GA4 measurement ID is now quoted (`| tojson`); it was emitted as a
  bare JS expression (`ReferenceError`). The Google Tag Manager snippet is emitted only when
  `GA_GTM_CONTAINER_ID` is set, instead of always requesting `gtm.js?id=`. An optional
  `GOOGLE_ANALYTICS_CONFIG` dict is passed as the third argument to `gtag('config', ...)`.

To update, copy the `pelican-bootstrap3/` directory from a newer commit, update the commit above,
and re-apply the patches if upstream has not fixed them.

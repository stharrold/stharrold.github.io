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

To update, copy the `pelican-bootstrap3/` directory from a newer commit, update the commit above,
and re-apply the patches if upstream has not fixed them.

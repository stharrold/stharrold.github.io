#!/usr/bin/env python
# -*- coding: utf-8 -*- #
r"""Configuration settings for pelican.

See Also:
    publishconf.py

Notes:
    * Settings are defined in order from pelican docs.[^pel]
    * Undefined settings have default values from pelican docs.[^pel]

References:
    [^pel]: https://docs.getpelican.com/en/4.12.0/settings.html

"""


# Basic settings
AUTHOR = 'Samuel Harrold'
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
# Remove all old files and directories when building.
DELETE_OUTPUT_DIRECTORY = True
# Markdown extensions from https://python-markdown.github.io/extensions/
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.toc': {'title': 'Contents', 'baselevel': 2}},
    'output_format': 'html5'}
PATH = 'content'
SITENAME = 'Data Science Demos'
# Define SITEURL only when publishing to test relative links.
SITEURL = ''
STATIC_PATHS = ['static', 'extra/robots.txt']
# For search engines using `robots.txt`:
# https://github.com/getpelican/pelican/wiki/Tips-n-Tricks
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'}}
ARTICLE_EXCLUDES = STATIC_PATHS
TIMEZONE = 'Etc/UTC'
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'archives']


# Plugin settings
# Namespace plugins from https://github.com/pelican-plugins are installed by
#     `uv sync` (see pyproject.toml) and load by short name.
# 'pelican_alias' is a local Python 3 port in plugins/ of
#     https://github.com/Nitron/pelican-alias
# Note: An explicit PLUGINS list disables namespace plugin auto-discovery,
#     so every plugin must be listed.
# Note: liquid_tags.notebook has been disabled since it does not
#     render cleanly with pelican-bootstrap3. Also collapse code does not
#     function with pelican-bootstrap3, ipython v4.0.0, pelicanhtml_[3,3.1].tpl
#     NOTEBOOK_DIR = 'static'
#     pelican-bootstrap3 does not require EXTRA_HEADER to include the notebook. 
# TODO: Experiment with Google Custom Search vs tipue_search.
#     https://github.com/stharrold/stharrold.github.io/issues/8
# TODO: Add embed_html as plugin
#     https://github.com/stharrold/stharrold.github.io/issues/5
# TODO: PLUGINS = ['ga_page_view', 'embed_html']
PLUGIN_PATHS = ['plugins']
PLUGINS = ['i18n_subsites', 'related_posts', 'tag_cloud', 'tipue_search', 'render_math', 'pelican_alias']
# For 'i18n_subsites':
#     pelican-bootstrap3 templates use `_()` and `{% trans %}`, which need
#     the jinja2 i18n extension and the translations installed by this plugin.
#     The dict replaces pelican's default, so keep its whitespace settings.
JINJA_ENVIRONMENT = {'trim_blocks': True, 'lstrip_blocks': True, 'extensions': ['jinja2.ext.i18n']}
# For 'related_posts':
RELATED_POSTS_MAX = 5
# For 'tag_cloud':
TAG_CLOUD_SORTING = 'alphabetically'
# For 'tipue_search':
#     pelican-bootstrap3 requires 'search' in DIRECT_TEMPLATES.
#     The plugin writes `tipuesearch_content.js` for the Tipue Search 7.0
#         files bundled with pelican-bootstrap3.
DIRECT_TEMPLATES.append('search')
# For 'render_math':
MATH_JAX = {'align': 'left'}


# URL settings
# Required by pelican-boostrap3 to resolve "Tags" and "Categories" links.
CATEGORIES_URL = 'categories.html'
TAGS_URL = 'tags.html'


# Feed settings
# All other feed settings are default to `None`.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
TRANSLATION_FEED_ATOM = None


# Theme settings
# Vendored from https://github.com/getpelican/pelican-themes (see themes/README.md)
THEME = 'themes/pelican-bootstrap3'
DISQUS_SITENAME = 'stharroldgithubio'
GOOGLE_ANALYTICS = 'UA-43020842-2'
# TODO: Explore Google Universal Analytics options.
#GOOGLE_ANALYTICS_UNIVERSAL = ''
#GOOGLE_ANALYTICS_UNIVERSAL_PROPERTY = ''
BOOTSTRAP_THEME = 'flatly'
SHOW_ARTICLE_CATEGORY = True
SHOW_DATE_MODIFIED = True
PYGMENTS_STYLE = 'default'
DISPLAY_BREADCRUMBS = True
# TODO: Make a FAVICON
DISPLAY_ARTICLE_INFO_ON_INDEX = True
DISPLAY_TAGS_ON_SIDEBAR = True
DISPLAY_TAGS_INLINE = True
DISPLAY_CATEGORIES_ON_SIDEBAR = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
RECENT_POST_COUNT = 5
DISQUS_DISPLAY_COUNTS = True
CC_LICENSE_DERIVATIVES = 'yes'
CC_LICENSE_COMMERCIAL = 'yes'

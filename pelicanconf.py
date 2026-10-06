#!/usr/bin/env python
r"""Configuration settings for pelican.

See Also:
    publishconf.py

Notes:
    * Settings are defined in order from pelican docs.[^pel]
    * Undefined settings have default values from pelican docs.[^pel]

References:
    [^pel]: https://docs.getpelican.com/en/4.12.0/settings.html

"""

import datetime

# Basic settings
AUTHOR = "Samuel Harrold"
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
# Remove all old files and directories when building.
DELETE_OUTPUT_DIRECTORY = True
# Markdown extensions from https://python-markdown.github.io/extensions/
MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.codehilite": {"css_class": "highlight"},
        "markdown.extensions.extra": {},
        "markdown.extensions.toc": {"title": "Contents", "baselevel": 2},
        # Math as $...$ and $$...$$, rendered by MathJax 4 (theme includes/math.html).
        #     smart_dollar (default) ignores prices like "$20 per month".
        "pymdownx.arithmatex": {"generic": True},
    },
    "output_format": "html5",
}
PATH = "content"
SITENAME = "Data Science Demos"
# Define SITEURL only when publishing to test relative links.
SITEURL = ""
STATIC_PATHS = ["static", "extra/robots.txt", "extra/favicon.ico", "extra/favicon.png", "extra/apple-touch-icon.png"]
# For search engines using `robots.txt`:
# https://github.com/getpelican/pelican/wiki/Tips-n-Tricks
# Favicons go at the site root because browsers request `/favicon.ico` directly.
EXTRA_PATH_METADATA = {
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/favicon.ico": {"path": "favicon.ico"},
    "extra/favicon.png": {"path": "favicon.png"},
    "extra/apple-touch-icon.png": {"path": "apple-touch-icon.png"},
}
ARTICLE_EXCLUDES = STATIC_PATHS
TIMEZONE = "Etc/UTC"
DIRECT_TEMPLATES = ["index", "tags", "categories", "archives"]


# Plugin settings
# Namespace plugins from https://github.com/pelican-plugins are installed by
#     `uv sync` (see pyproject.toml) and load by short name.
# 'pelican_alias' is a local Python 3 port in plugins/ of
#     https://github.com/Nitron/pelican-alias
# Note: An explicit PLUGINS list disables namespace plugin auto-discovery,
#     so every plugin must be listed.
# TODO: Add embed_html as plugin
#     https://github.com/stharrold/stharrold.github.io/issues/5
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["related_posts", "tag_cloud", "pelican_alias"]
# For 'related_posts':
RELATED_POSTS_MAX = 5
# For 'tag_cloud':
TAG_CLOUD_SORTING = "alphabetically"
# Site search: search.html loads the Pagefind index, which is built from
#     output/ after Pelican runs (`uv run python -m pagefind --site output`).
DIRECT_TEMPLATES.append("search")


# URL settings
# Used by the theme for "Tags" and "Categories" links.
CATEGORIES_URL = "categories.html"
TAGS_URL = "tags.html"


# Feed settings
# All other feed settings are default to `None`.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
TRANSLATION_FEED_ATOM = None


# Theme settings
# Bootstrap 5 theme forked from pelican-bootstrap3 (see themes/README.md).
THEME = "themes/datasciencedemos"
DISQUS_SITENAME = "stharroldgithubio"
# Google Analytics 4 is set only in publishconf.py so local builds are not tracked.
#     The Universal Analytics property UA-43020842-2 stopped collecting on 2023-07-01.
GOOGLE_ANALYTICS = None
# Articles last updated at least this many years before the build year show an outdated-content notice.
BUILD_YEAR = datetime.date.today().year
OUTDATED_AFTER_YEARS = 5
SHOW_ARTICLE_CATEGORY = True
SHOW_DATE_MODIFIED = True
PYGMENTS_STYLE = "default"
DISPLAY_BREADCRUMBS = True
# "DS" monogram in the flatly navbar color (#2C3E50); files are in content/extra/.
FAVICON = "favicon.png"
TOUCHICON = "apple-touch-icon.png"
DISPLAY_ARTICLE_INFO_ON_INDEX = True
DISPLAY_TAGS_ON_SIDEBAR = True
DISPLAY_CATEGORIES_ON_SIDEBAR = True
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True
RECENT_POST_COUNT = 5

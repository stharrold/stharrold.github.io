#!/usr/bin/env python
# -*- coding: utf-8 -*- #
r"""Configuration settings for pelican.

See Also:
    publishconf.py

Notes:
    * Settings are defined in order from [1]_.
    * Undefined settings have default values from [1]_.

References:
    .. [1] http://docs.getpelican.com/en/3.6.3/settings.html

"""


# Import standard packages.
import os
import warnings


# Basic settings
AUTHOR = 'Samuel Harrold'
DISPLAY_PAGES_ON_MENU = True
DISPLAY_CATEGORIES_ON_MENU = False
# Remove all old files and directories when building.
DELETE_OUTPUT_DIRECTORY = True
# Markdown extensions from http://pythonhosted.org/Markdown/extensions/index.html
MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'extra', 'toc(title=Table of contents, baselevel=2)']
PATH = 'content'
SITENAME = 'Data Science Demos'
# Define SITEURL only when publishing to test relative links.
SITEURL = ''
STATIC_PATHS = ['static']
ARTICLE_EXCLUDES = STATIC_PATHS
TIMEZONE = 'Etc/UTC'
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'archives']


# Plugin settings
# From https://github.com/getpelican/pelican-plugins
# TODO: Experiment with Google Custom Search vs tipue_search.
# TODO: Add embed_html as pelican-plugins-dev/embed_html
# https://github.com/stharrold/stharrold.github.io/issues/5
# TODO: PLUGIN_PATHS = ['pelican-plugins-dev']
# TODO: PLUGINS = ['ga_page_view', 'embed_html']
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['related_posts', 'tag_cloud', 'tipue_search', 'liquid_tags.notebook']
RELATED_POSTS_MAX = 5
TAG_CLOUD_SORTING = 'alphabetically'
# tipue_search: pelican-bootstrap3 requires 'search' in DIRECT_TEMPLATES
DIRECT_TEMPLATES.append('search')
NOTEBOOK_DIR = 'static'
# liquid_tags.notebook: pelican-bootstrap3 does not require EXTRA_HEADER to include the notebook. 
# liquid_tags.notebook: Collapse code does not function with pelican-bootstrap3, ipython v4.0.0, pelicanhtml_[3,3.1].tpl


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
# From https://github.com/getpelican/pelican-themes
THEME = 'pelican-themes/pelican-bootstrap3'
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
CC_LICENSE_DERIVATIVES = "yes"
CC_LICENSE_COMMERCIAL = "yes"

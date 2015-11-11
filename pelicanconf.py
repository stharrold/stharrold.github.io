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


# Basic settings
AUTHOR = 'Samuel Harrold'
DISPLAY_CATEGORIES_ON_MENU = False
# Remove all old files and directories when building.
DELETE_OUTPUT_DIRECTORY = True
PATH = 'content'
# From https://github.com/getpelican/pelican-plugins
# and https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['liquid_tags.img']
SITENAME = 'Data Science Demos'
# Define SITEURL only when publishing to test relative links.
SITEURL = ''
STATIC_PATHS = ['images', 'notebooks']
ARTICLE_EXCLUDES = STATIC_PATHS
TIMEZONE = 'Etc/UTC'
DIRECT_TEMPLATES = ['index', 'categories', 'tags', 'archives', 'authors']

# Feed settings
# Disable feed generation for developing.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Translations
TRANSLATION_FEED_ATOM = None

# Themes
# For themes, see https://github.com/getpelican/pelican-themes
#DISQUS_SITENAME = ''
GITHUB_URL = 'https://github.com/stharrold/stharrold.github.io'
#GOOGLE_ANALYTICS = 'UA-XXXX-YYYY'
# Note: As of 2015-11-10, categories.html does not render correctly for
# Pelican's default theme, 'notmyidea'. The html format file is missing
# from the theme: https://github.com/getpelican/pelican/issues/1450
MENUITEMS = [
    ('Categories', '/categories.html'),
    ('Tags', '/tags.html'),
    ('Archives', '/archives.html'),
    ('Search', 'https://www.google.com/?q=site:stharrold.github.io'),
    ('Authors', '/authors.html')]
SOCIAL = [
    ('stharrold', 'https://github.com/stharrold'),
    ('Samuel Harrold', 'https://www.linkedin.com/in/samuelharrold'),
    ('stharrold', 'https://twitter.com/stharrold'),
    ('Samuel Harrold', 'https://plus.google.com/+SamuelHarrold')]

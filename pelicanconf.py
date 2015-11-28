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
DISPLAY_CATEGORIES_ON_MENU = False
# Remove all old files and directories when building.
DELETE_OUTPUT_DIRECTORY = True
PATH = 'content'
# From https://github.com/getpelican/pelican-plugins
# and https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['liquid_tags.notebook']
# Default open mode is to read text encoded as utf-8.
if os.path.exists('_nb_header.html'):
    EXTRA_HEADER = open('_nb_header.html').read()
else:
    warnings.warn(
        "\nRun `pelican --settings [pelican,publish]conf.py` again to format the IPython notebook content within the blog posts.")
SITENAME = 'Data Science Demos'
# Define SITEURL only when publishing to test relative links.
SITEURL = ''
STATIC_PATHS = ['images', 'notebooks']
ARTICLE_EXCLUDES = STATIC_PATHS
TIMEZONE = 'Etc/UTC'
DIRECT_TEMPLATES = ['index', 'categories', 'tags', 'archives']


# Feed settings
# Disable feed generation for developing.
# All other feed settings are default to `None`.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


# Translations
TRANSLATION_FEED_ATOM = None


# Themes
# From https://github.com/getpelican/pelican-themes
# and https://github.com/getpelican/pelican-themes/tree/master/octopress
THEME = 'pelican-themes/octopress'
SEARCH_BOX = True
DISPLAY_FEEDS_ON_MENU = False
#DISQUS_SITENAME = ''
GITHUB_URL = 'https://github.com/stharrold/stharrold.github.io'
#GOOGLE_ANALYTICS = 'UA-XXXX-YYYY'
MENUITEMS = [
    ('Archives', '/archives.html')]
SOCIAL = [
    ('GitHub: stharrold', 'https://github.com/stharrold'),
    ('LinkedIn: Samuel Harrold', 'https://www.linkedin.com/in/samuelharrold'),
    ('Twitter: stharrold', 'https://twitter.com/stharrold'),
    ('Google+: Samuel Harrold', 'https://plus.google.com/+SamuelHarrold')]

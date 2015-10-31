#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Options from pelican-quickstart
AUTHOR = 'Samuel Harrold'
SITENAME = 'Data Science Demos'
SITEURL = ''
PATH = 'content'
TIMEZONE = 'Etc/UTC'
DEFAULT_LANG = 'en'
DEFAULT_PAGINATION = 10

# Disable feed generation for developing.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('"Data Science Demos" source code', 'https://github.com/stharrold/stharrold.github.io'),)

# Social widgets
SOCIAL = (('stharrold', 'https://github.com/stharrold'),
          ('Samuel Harrold', 'https://www.linkedin.com/in/samuelharrold'),
          ('stharrold', 'https://twitter.com/stharrold'),
          ('Samuel Harrold', 'https://plus.google.com/+SamuelHarrold'),)

# Theme
# https://github.com/duilio/pelican-octopress-theme
THEME = 'pelican-themes/octopress'
SEARCH_BOX = True

# # Plugins
# # https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags
# PLUGIN_PATH = 'pelican-plugins'
# PLUGINS = ['liquid_tags.notebook']
# NOTEBOOK_DIR = 'notebooks'

# Regenerate output while developing.
DELETE_OUTPUT_DIRECTORY = True

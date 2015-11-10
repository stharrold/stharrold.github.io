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
# Remove all old files and directories when building.
DELETE_OUTPUT_DIRECTORY = True
PATH = 'content'
# Plugins
# Plugin added as a submodule.
# # https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags
# PLUGINS = ['liquid_tags.notebook']
# PLUGIN_PATHS = 'pelican-plugins'
# NOTEBOOK_DIR = 'notebooks'
SITENAME = 'Data Science Demos'
# Define SITEURL only when publishing.
SITEURL = ''
TIMEZONE = 'Etc/UTC'

# Feed settings
# Disable feed generation for developing.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Translations
TRANSLATION_FEED_ATOM = None

# Themes
# Using default theme.
# To use a custom theme, add themes as a git submodule:
# $ git submodule add --recursive https://github.com/getpelican/pelican-themes.git
# https://git-scm.com/book/en/v2/Git-Tools-Submodules
# To delete the submodule: https://gist.github.com/kyleturner/1563153
#DISQUS_SITENAME = ''
GITHUB_URL = 'https://github.com/stharrold/stharrold.github.io_source'
#GOOGLE_ANALYTICS = 'UA-XXXX-YYYY'
SOCIAL = (
    ('stharrold', 'https://github.com/stharrold'),
    ('Samuel Harrold', 'https://www.linkedin.com/in/samuelharrold'),
    ('stharrold', 'https://twitter.com/stharrold'),
    ('Samuel Harrold', 'https://plus.google.com/+SamuelHarrold'),)

#!/usr/bin/env python
# -*- coding: utf-8 -*- #
r"""Configuration settings for publishing with pelican.

See Also:
    pelicanconf.py

Notes:
    * Settings are defined in order from [1]_.
    * Minimal settings from `pelicanconf.py` are changed.

References:
    .. [1] http://docs.getpelican.com/en/3.6.3/settings.html

"""

# Import standard packages.
import os
import sys
# Add current directory to module search path.
sys.path.append(os.curdir)
# Import local modules.
from pelicanconf import *


# Basic settings
SITEURL = 'https://stharrold.github.io'


# Feed settings
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'

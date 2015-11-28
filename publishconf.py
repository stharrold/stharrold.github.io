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
# As of 2015-10-30, LinkedIn requires RSS: Profile > Contact Info > Websites
FEED_DOMAIN = SITEURL
FEED_ATOM = 'feeds/atom.xml'
FEED_RSS = 'feeds/rss.xml'

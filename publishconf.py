#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# Site to publish.
SITEURL = 'https://stharrold.github.io'
RELATIVE_URLS = False

# Feeds
# As of 2015-10-30, LinkedIn requires RSS: Profile > Contact Info > Websites
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""

#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Global Watchpost LLC'
SITENAME = 'List Cloud Regions'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'UTC'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

PLUGINS = [ 'list_cloud_regions', ]
PLUGIN_PATHS = [ 'plugins', ]

THEME = "./theme"

TAGS_SAVE_AS = None
CATEGORIES_SAVE_AS = None
AUTHORS_SAVE_AS = None
ARCHIVES_SAVE_AS = None
INDEX_SAVE_AS = None

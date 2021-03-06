# This file is used to store your site specific settings
# for database access.
# It also store satchmo unique information
#
#
# Modify this file to reflect your settings, then rename it to
# local_settings.py
#
# This file is helpful if you have an existing Django project.
# These are specific things that Satchmo will need.
# you MUST make sure these settings are imported from your project settings file!

import os
import logging

# This is useful, since satchmo is not the "current directory" like load_data expects.
# SATCHMO_DIRNAME = ''

# Only set these if Satchmo is part of another Django project
# SITE_NAME = ''
# ROOT_URLCONF = ''
# MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
# DJANGO_PROJECT = 'Your Main Project Name'
# DJANGO_SETTINGS_MODULE = 'main-project.settings'
# DATABASE_NAME = ''
# DATABASE_PASSWORD = ''
# DATABASE_USER = ''
# SECRET_KEY = ''

##### For Email ########
# If this isn't set in your settings file, you can set these here
# EMAIL_HOST = 'host here'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'your user here'
# EMAIL_HOST_PASSWORD = 'your password'
# EMAIL_USE_TLS = True

#### Satchmo unique variables ####

# These are used when loading the test data
SITE_DOMAIN = "example.com"
SITE_NAME = "My Site"

from django.conf.urls import *

# These can override or add to the default URLs
from django.conf.urls import *

URLS = []

# a cache backend is required.  Do not use locmem, it will not work properly at all in production
# Preferably use memcached, but file or DB is OK.  File is faster, I don't know why you'd want to use
# db, personally.  See: http://www.djangoproject.com/documentation/cache/ for help setting up your
# cache backend
# CACHE_BACKEND = "memcached://127.0.0.1:11211/"
# CACHE_BACKEND = "file:///var/tmp/django_cache"
CACHE_TIMEOUT = 60 * 5

# modify the cache_prefix if you have multiple concurrent stores.
CACHE_PREFIX = "STORE"


# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-gb"

# Languages for your site.  The language name
# should be the utf-8 encoded local name for the language.


def gettext_noop(s):
    return s


LANGUAGES = (("en", "English"),)

# Locale path settings.  Needs to be set for Translation compilation.
# It can be blank
# LOCALE_PATHS = ""

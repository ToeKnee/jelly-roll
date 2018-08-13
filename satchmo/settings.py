# Django settings for satchmo project.
# If you have an existing project, then ensure that you modify local_settings-customize.py
# and import it from your main settings file. (from local_settings import *)
import os

DIRNAME = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))

DJANGO_PROJECT = 'satchmo'
DJANGO_SETTINGS_MODULE = 'satchmo.settings'

LOCAL_DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ''),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'jelly-roll.db',
    }
}

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
# For windows, you must use 'us' instead
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# Image files will be stored off of this path.
MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
# URL that handles the media served from MEDIA_ROOT. Use a trailing slash.
# Example: "http://media.lawrence.com/"
MEDIA_URL = '/static/'
# URL that handles the media served from SSL.  You only need to set this
# if you are using a non-relative url.
# Example: "https://media.lawrence.com"
# MEDIA_SECURE_URL = "https://foo.com/"
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'Make this unique, and dont share it with anybody.'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

# This is used to add additional config variables to each request
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "satchmo.shop.context_processors.settings",
)

ROOT_URLCONF = 'satchmo.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    os.path.join(DIRNAME, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',

    'satchmo',
    'satchmo.caching',
    'satchmo.configuration',
    'satchmo.contact',
    'satchmo.currency',
    'satchmo.discount',
    'satchmo.fulfilment',
    'satchmo.l10n',
    'satchmo.payment',
    'satchmo.product',
    'satchmo.product.brand',
    'satchmo.shipping',
    'satchmo.shipping.modules.tieredweightzone',
    'satchmo.shop',
    'satchmo.tax',
    'satchmo.upsell',
    'satchmo.wishlist',
    'satchmo.giftcertificate',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PROFILE_MODULE = 'contact.Contact'

# Exchange Rate settings
EXCHANGE_RATE_MODULE = 'ecb'
FIXERIO_KEY = ''

SATCHMO_SETTINGS = {
    # this will override any urls set in the store url modules
    # 'SHOP_URLS' : satchmo.shop.views,
    #    (r'^checkout/pay/$', 'paypal.checkout_step2.pay_ship_info', {}, 'satchmo_checkout-step2'),
    #    (r'^checkout/confirm/$', 'paypal.checkout_step3.confirm_info', {}, 'satchmo_checkout-step3'),
    #   if you have satchmo.feeds, make sure to include its URL
    #    (r'^feed/', include('satchmo.feeds.urls')),
    #   enable brands here
    #    (r'^brand/', include('satchmo.product.brand.urls'))
    # }

    # This is the base url for the shop.  Only include a leading slash
    # examples: '/shop' or '/mystore'
    # If you want the shop at the root directory, set SHOP_BASE to ''
    'SHOP_BASE': '/store',

    # This will turn on/off product translations in the admin for products
    'ALLOW_PRODUCT_TRANSLATIONS': True,

    # register custom external payment modules by listing their modules here
    # ex: 'CUSTOM_PAYMENT_MODULES' : ['client.payment.wondercharge',]
    'CUSTOM_PAYMENT_MODULES': [],

    # register custom external shipping modules by listing their modules here
    # ex: 'CUSTOM_SHIPPING_MODULES' : ['client.shipping.fancyshipping',]
    'CUSTOM_SHIPPING_MODULES': [],

    # register custom external product modules by listing their modules here
    # ex: 'CUSTOM_PRODUCT_MODULES' : ['client.product.myproducttype',]
    'CUSTOM_PRODUCT_MODULES': [],
}

# Load the local settings
from .local_settings import *

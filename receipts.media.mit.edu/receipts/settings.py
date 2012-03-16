# Django settings for receipts project.
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DEPLOY = False

if DEPLOY:
    HOST_NAME = "receipts.media.mit.edu"
else:
    HOST_NAME = "receipts-dev.media.mit.edu"
#PREFIX = "/home/www/receipts.media.mit.edu/"

LOGIN_REDIRECT_URL = "/web/"

if DEPLOY:
    pass
else:
    # receipts Facebook Connect app
    FACEBOOK_API_KEY = '884174aa5f817f3f1f62dc204bfbb181'
    FACEBOOK_SECRET_KEY = 'd258970fe9b9efcb6a02ac0d21d60b9b'
FACEBOOK_INTERNAL = True
FACEBOOK_CACHE_TIMEOUT = 1800
NUM_FRIEND_RETRIEVE_LIMIT = 50


# Full path to the APN Certificate / Private Key .pem
IPHONE_SANDBOX_APN_PUSH_CERT = os.path.join(PROJECT_ROOT, "iphone_ck.pem")
IPHONE_LIVE_APN_PUSH_CERT = os.path.join(PROJECT_ROOT, "iphone_live.pem")

# Set this to the hostname for the outgoing push server
IPHONE_SANDBOX_APN_HOST = 'gateway.sandbox.push.apple.com'
IPHONE_LIVE_APN_HOST = 'gateway.push.apple.com'

# Set this to the hostname for the feedback server
IPHONE_SANDBOX_FEEDBACK_HOST = 'feedback.sandbox.push.apple.com'
IPHONE_LIVE_FEEDBACK_HOST = 'feedback.push.apple.com'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'Receipts'             # Or path to database file if using sqlite3.
DATABASE_USER = 'otnpostgres'             # Not used with sqlite3.
DATABASE_PASSWORD = 'q0p1w9o2'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/www/receipts.media.mit.edu/receipts/static/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://%s/media/'%HOST_NAME

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'if5k@t)b_*#%5p@)5)np%qi_p1b2e@u^kk$qzogn1bcknz=$8k'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'facebook.djangofb.FacebookMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'facebookconnect.middleware.FacebookConnectMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'facebookconnect.models.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

if DEPLOY:
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
    # TODO: python manage.py createcachetable [receipts_cache_table]
    #CACHE_BACKEND = 'db://receipts_cache_table'
    CACHE_MIDDLEWARE_SECONDS = 1800
    CACHE_MIDDLEWARE_KEY_PREFIX = 'receipts'

ROOT_URLCONF = 'receipts.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/www/receipts.media.mit.edu/receipts',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'tagging',
    'facebookconnect',
    'finance',
    'web',
    'common',
    'shoebox',
    'iphonepush',
    'south',
)

DUMMY_FACEBOOK_INFO = {
    'uid':0,
    'name':'(Private)',
    'first_name':'(Private)',
    'pic_square_with_logo':'http://www.facebook.com/pics/t_silhouette.gif',
    'affiliations':None,
    'status':None,
    'proxied_email':None,
}

try:
    LOCAL_DEVELOPMENT = False
    from local_settings import *
    LOCAL_DEVELOPMENT = True
except ImportError:
    try:
        from mod_python import apache
        apache.log_error('local_settings.py not set; using default settings', apache.APLOG_NOTICE)
    except ImportError:
        import sys
        sys.stderr.write('local_settings.py not set; using default settings\n')

import logging
import logging.config

try:
    logging.config.fileConfig(PREFIX+"receipts/logging.conf")
    # create logger
    LOGGER = logging.getLogger("receipts")
except:    
    pass




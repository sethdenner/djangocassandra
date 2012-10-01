# Django settings for web project.

# Set pythonpath to look at shared modules
import os
import sys
PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../share"))

SERVICE_NAME = 'Knotis'

PRICE_MERCHANT_MONTHLY = 14.

BUSINESS_NAME_BLACKLIST = (
    'facebook',
    'login',
    'plans',
    'contact',
    'about',
    'howitworks',
    'story',
    'inquire',
    'support',
    'terms',
    'privacy',
    'events',
    'happyhours',
    'dashboard',
    'offer',
    'offers',
    'business',
    'update',
    'get_expiring_offers',
    'get_newest_offers',
    'get_popular_offers',
    'get_offer_by_status',
    'profile',
    'subscriptions',
    'qrcode',
    'media',
    'auth',
    'signup',
    'forgotpassword',
    'passwordreset',
    'admin',
    'api',
    'paypal',
    'neighborhood',
)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.googlemail.com'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

YELP_API_URI = 'http://api.yelp.com/v2/business/'
YELP_CONSUMER_KEY = 'FOe0SiqTLG-KTzXpg7fdxQ'
YELP_CONSUMER_SECRET = 'vfyr5UHPQbjN5QFz22PcckRODSE'
YELP_TOKEN_KEY = 'MEMHpkNVdQHmqK6fjjf0Xls30yAdg6sC'
YELP_TOKEN_SECRET = 'WQyffYaB4R-NaMGaTcHJOkUWsWE'

TWITTER_FEED_URI_TEMPLATE = (
    'https://api.twitter.com/1/statuses/user_timeline.json'
    '?include_entities=true'
    '&include_rts=true'
    '&screen_name=%s'
    '&count=%s'
)
TWITTER_DEFAULT_RESULT_COUNT = 10

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = '0c7d8d59-318e-4d22-bd5d-6e146644339f'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$4kx&)iwyb22(kh=p0q(l&na6o!1-^vdzcy%j#n19^*l4(l#69'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
    'legacy.authentication.backends.LegacyAuthenticationBackend',
)

AUTOLOAD_SITECONF = 'dbindexer'

INSTALLED_APPS = (
    # Third party Django apps.
    'autoload',
    'dbindexer',
    'piston',
    'djangotoolbox',
    'permission_backend_nonrel',
    'background_task',
    'timezones',
    'sorl.thumbnail',
    # Django standard apps.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    # Knotis apps.
    'manytomanynonrel',
    'foreignkeynonrel',
    'paypal',
    'facebook',
    'knotis_yelp',
    'knotis_twitter',
    'knotis_auth',
    'knotis_maps',
    'knotis_contact',
    'knotis_happyhour',
    'knotis_highchart',
    'knotis_events',
    'knotis_qrcodes',
    'legacy',
    'app',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Import additional settings.
ENVIRONMENT_NAME = 'dev'

# You can key the configurations off of anything - I use project path.
configs = {
    'dev': 'dev',
    'int': 'int',
    'prod': 'prod'
}

# Import the configuration settings file - REPLACE projectname with your project
config_module = __import__(
    'config.%s' % configs[ENVIRONMENT_NAME],
    globals(),
    locals(),
    'web'
)

# Load the config settings properties into the local scope.
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)

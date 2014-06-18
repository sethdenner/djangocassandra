import os


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SERVICE_NAME = 'Knotis'

PRICE_MERCHANT_MONTHLY = 14.

EMAIL_COMPLETED_OFFERS_INTERVAL_DAYS = 7

PASSWORD_RESET_EXPIRE_MINUTES = 10080

FORMAT_MODULE_PATH = 'formats'
DATE_FORMAT = 'm/d/Y'        # '10/25/06'
TIME_FORMAT = 'h:i:s A'      # '02:30:59 PM'
DATETIME_FORMAT = ' '.join([DATE_FORMAT, TIME_FORMAT])

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

PRIORITY_BUSINESS_NAMES = [
    'cupcake-royale-captiol-hill',
    'brooks-brothers',
    'via-tribunali---capitol-hill',
    'caffe-vita-capitol-hill',
    'paramount-theatre',
    'teatro-zinzanni',
    'lunch-box-laboratory-south-lake-union',
    'elysian-brewing-co.-capitol-hill',
    'macrina-bakery',
    'paseo-caribbean-restaurant',
    'easy-street-records',
    'verbovski-photography',
    'zpizza',
    'mountain-to-sound-outfitters',
    'calico-healthy-skin-and-waxing',
    'blue-highway-games',
    'throwbacks-northwest',
    'lab5-fitness',
    'sugarpill',
    'homestreet-bank',
    'cactus-madison-park',
    'pirkko',
    'umi-sake-house',
    'scraps-dog-bakery-and-boutique',
    'cherry-consignment',
    'dr.-peter-h.-yi-dds-ps',
    'green-leaf-belltown',
    'ipic-theaters'
]

CRISPY_TEMPLATE_PACK = 'bootstrap'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


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
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$4kx&)iwyb22(kh=p0q(l&na6o!1-^vdzcy%j#n19^*l4(l#69'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'knotis.template.loaders.app_directories.Loader'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'knotis.contrib.mobile.middleware.MobileDetectionMiddleware',
    'knotis.contrib.activity.middleware.ActivityMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
    'knotis.contrib.auth.authentication.backends.CaseInsensitiveUsernameAuthenticationBackend',
    'knotis.contrib.endpoint.authentication.backends.EndpointValidationAuthenticationBackend',
    'knotis.contrib.legacy.authentication.backends.LegacyAuthenticationBackend',
    'knotis.contrib.legacy.authentication.backends.HamburgertimeAuthenticationBackend'
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'doac.contrib.rest_framework.authentication.DoacAuthentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'knotis.contrib.api.views.knotis_exception_handler'
}

AUTOLOAD_SITECONF = 'dbindexer'

INSTALLED_APPS = (
    'knotis',
    # Third party Django apps.
    'autoload',
    'dbindexer',
    'djangotoolbox',
    'django_extensions',
    'permission_backend_nonrel',
    'timezones',
    'sorl.thumbnail',
    'crispy_forms',
    'haystack',
    'corsheaders',
    'rest_framework',
    'doac',
    'test_utils',
    # Django standard apps.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    # knotis apps
    'knotis.contrib.layout',
    'knotis.contrib.search',
    'knotis.contrib.navigation',
    'knotis.contrib.denormalize',
    'knotis.contrib.auth',
    'knotis.contrib.endpoint',
    'knotis.contrib.bootstrap',
    'knotis.contrib.quick',
    'knotis.contrib.identity',
    'knotis.contrib.relation',
    'knotis.contrib.activity',
    'knotis.contrib.offer',
    'knotis.contrib.transaction',
    'knotis.contrib.inventory',
    'knotis.contrib.product',
    'knotis.contrib.media',
    'knotis.contrib.maps',
    'knotis.contrib.location',
    'knotis.contrib.wizard',
    'knotis.contrib.merchant',
    'knotis.contrib.consumer',
    'knotis.contrib.qrcode',
    'knotis.contrib.api',
    'knotis.contrib.legacy',
    'knotis.contrib.facebook',
    'knotis.contrib.twitter',
    'knotis.contrib.stripe',
    'knotis.contrib.admintools',
)

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS'
)

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'current-identity'
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'console',
            'file'
        ],
    },
    'formatters': {
        'verbose': {
            'format': (
                '%(asctime)s|%(levelname)s|%(name)s.%(funcName)s|L%(lineno)s|%(message)s'
            )
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': '/srv/knotis/logs/django.log',
            'maxBytes': 1048576,
            'backupCount': 10
        }
    },
    'loggers': {
    },
}

# Import additional settings.
ENVIRONMENT_NAME = 'int'


# You can key the configurations off of anything - I use project path.
configs = {
    'dev': 'dev',
    'int': 'int',
    'prod': 'prod',
    'stage': 'stage',
}

"""
Import the configuration settings file
REPLACE projectname with your project
"""
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

import os


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SERVICE_NAME = 'Knotis'

PRICE_MERCHANT_MONTHLY = 14.

EMAIL_COMPLETED_OFFERS_INTERVAL_DAYS = 7

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

MIDDLEWARE_CLASSES = (
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'knotis.contrib.mobile.middleware.MobileDetectionMiddleware',
    'knotis.contrib.activity.middleware.ActivityMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
    'knotis.contrib.auth.authentication.backends.EndpointValidationAuthenticationBackend',
    'knotis.contrib.legacy.authentication.backends.LegacyAuthenticationBackend',
    'knotis.contrib.legacy.authentication.backends.HamburgertimeAuthenticationBackend'
)

AUTOLOAD_SITECONF = 'dbindexer'

INSTALLED_APPS = (
    # Third party Django apps.
    'autoload',
    'dbindexer',
    'piston',
    'djangotoolbox',
    'django_extensions',
    'permission_backend_nonrel',
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
    'knotis',
    'knotis.contrib.auth',
    'knotis.contrib.bootstrap',
    'knotis.contrib.quick',
    'knotis.contrib.identity',
    'knotis.contrib.relation',
    'knotis.contrib.activity'
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
            'filename': '/srv/knotis/logs/web.log',
            'maxBytes': 1048576,
            'backupCount': 10
        }
    },
    'loggers': {
    },
}

# Import additional settings.
ENVIRONMENT_NAME = 'seth'

# You can key the configurations off of anything - I use project path.
configs = {
    'dev': 'dev',
    'int': 'int',
    'prod': 'prod',
    'stage': 'stage',
    'seth': 'seth'
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

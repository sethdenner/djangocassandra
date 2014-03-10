DATABASES = {
    'default': {
        'ENGINE': 'django_cassandra.db', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'knotis', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.                                                                           
        'PORT': '', # Set to empty string for default. Not used with sqlite3.                                                                                       
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

EMAIL_BILLING_USER = 'billing@knotis.com'
EMAIL_HOST_USER = 'support@knotis.com'
EMAIL_HOST_PASSWORD = 'p0tent1al!'

# Base url for external access
BASE_URL = 'https://knotis.com'  # NO TRAILING SLASH!!!

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
STATIC_URL_ABSOLUTE = ''.join([
    BASE_URL,
    STATIC_URL
])

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/srv/knotis/app/static/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/srv/knotis/app/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
MEDIA_URL_ABSOLUTE = ''.join([
    BASE_URL,
    MEDIA_URL
])

GOOGLE_MAPS_API_KEY = 'AIzaSyBrsdJdU3pwYc5Rsbg7f25yOGNYaOmaFnk'

FACEBOOK_APP_ID = '630594820333282'
FACEBOOK_API_SECRET = 'afd1055a3239d50409877e72ef81382e'
FACEBOOK_DEFAULT_SCOPE = 'publish_stream,manage_pages,publish_actions'
FACEBOOK_API_URL = 'https://graph.facebook.com'

PAYPAL_ACCOUNT = 'billing@knotis.com'
PAYPAL_URL = 'https://www.paypal.com/cgi-bin/webscr'
PAYPAL_TEST_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_NOTIFY_URL = ''.join([
    BASE_URL,
    '/paypal/ipn/'
])
PAYPAL_PREMIUM_BUTTON_ID = 'RGN2J9C8A4MY4'
PAYPAL_DEFAULT_BUTTON_TEXT = 'Finish in Paypal'
PAYPAL_ITEM_SUBSCRIPTION = 'subscription'
PAYPAL_TRANSACTION_PRICE = 0.45

PRICE_MERCHANT_MONTHLY = 14.

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

YELP_API_URI = 'http://api.yelp.com/v2/business/'
YELP_CONSUMER_KEY = 'FOe0SiqTLG-KTzXpg7fdxQ'
YELP_CONSUMER_SECRET = 'vfyr5UHPQbjN5QFz22PcckRODSE'
YELP_TOKEN_KEY = 'MEMHpkNVdQHmqK6fjjf0Xls30yAdg6sC'
YELP_TOKEN_SECRET = 'WQyffYaB4R-NaMGaTcHJOkUWsWE'

TWITTER_CONSUMER_KEY = 'F1JxtuDONa6Iy4rF3cl7w'
TWITTER_CONSUMER_SECRET = '8BoRFGcveB6Q7Ber70uoNGQoZo3kSFKTm0kk5ICXo0'
TWITTER_KNOTIS_ACCESS_TOKEN = (
    '321699338-nji3k08VXK0Gu7YLmBXsk8ptU8yuxGaO3He560Nj'
)
TWITTER_KNOTIS_TOKEN_SECRET = '2NC4yOFFbXPR59VoXISuVsn5IoZrENo8yfvlaW1Y'
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_FEED_URL = (
    'https://api.twitter.com/1.1/statuses/user_timeline.json'
)
TWITTER_DEFAULT_RESULT_COUNT = 10

STRIPE_API_KEY = 'pk_live_rLgV1rfwNIZbNyHhATmitdSJ'
STRIPE_API_SECRET = 'sk_live_5eCJauCVIUiAnBcCeYUq6cVD'
STRIPE_MODE_PERCENT = 0.029
STRIPE_MODE_FLAT = 0.30

KNOTIS_MODE_PERCENT = 0.05 

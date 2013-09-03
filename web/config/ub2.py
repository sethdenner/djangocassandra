DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django_cassandra.db',
        'NAME': 'knotis',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

EMAIL_HOST_USER = 'knotis.dev@gmail.com'
EMAIL_HOST_PASSWORD = 'wheeling and dealing'

# Base url for external access
# NO TRAILING SLASH!!!
BASE_URL = 'http://ub2.knotis.com'

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

FACEBOOK_APP_ID = '227221503982317'
FACEBOOK_API_SECRET = 'c38d6b546822e6142d958d4e6f7c940d'
FACEBOOK_DEFAULT_SCOPE = 'email,user_about_me'
FACEBOOK_API_URL = 'https://graph.facebook.com'

PAYPAL_ACCOUNT = 'billing@knotis.com'
PAYPAL_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_TEST_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_NOTIFY_URL = ''.join([
    BASE_URL,
    '/paypal/ipn/'
])
PAYPAL_OFFER_BUTTON_ID = 'DCV66T4VPMMXU'
PAYPAL_PREMIUM_BUTTON_ID = 'YNYHC3S6TYB7W'
PAYPAL_DEFAULT_BUTTON_TEXT = 'Finish in Paypal'
PAYPAL_ITEM_SUBSCRIPTION = 'subscription'
PAYPAL_TRANSACTION_PRICE = 0.45

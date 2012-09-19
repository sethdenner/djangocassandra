
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django_cassandra.db', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.                                                     
        'NAME': 'knotis', # Or path to database file if using sqlite3.                                                                                                  
        'USER': '', # Not used with sqlite3.                                                                                                                            
        'PASSWORD': '', # Not used with sqlite3.                                                                                                                        
        'HOST': '74.121.189.162', # Set to empty string for localhost. Not used with sqlite3.                                                                           
        'PORT': '5551', # Set to empty string for default. Not used with sqlite3.                                                                                       
    }
}

EMAIL_HOST_USER = 'knotis.int@gmail.com'
EMAIL_HOST_PASSWORD = 'wheeling and dealing'

# Base url for external access
BASE_URL = 'http://wow3.knotis.com' # NO TRAILING SLASH!!!

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
STATIC_URL_ABSOLUTE = BASE_URL + STATIC_URL

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/srv/knotis/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://wow3.knotis.com/media/'

GOOGLE_MAPS_API_KEY = 'AIzaSyBrsdJdU3pwYc5Rsbg7f25yOGNYaOmaFnk'

FACEBOOK_APP_ID = '227221503982317'
FACEBOOK_API_SECRET = 'c38d6b546822e6142d958d4e6f7c940d'
FACEBOOK_DEFAULT_SCOPE = 'email,user_about_me'
FACEBOOK_API_URL = 'https://graph.facebook.com'

PAYPAL_ACCOUNT = 'billing@knotis.com'
PAYPAL_FORM_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_URL = 'ssl://www.sandbox.paypal.com'
PAYPAL_NOTIFY_URL = ''.join([
    BASE_URL,
    '/account/payment/'
])
PAYPAL_OFFER_BUTTON_ID = 'DCV66T4VPMMXU'
PAYPAL_PREMIUM_BUTTON_ID = 'YNYHC3S6TYB7W'
PAYPAL_DEFAULT_BUTTON_TEXT = 'Finish in Paypal'
PAYPAL_ITEM_SUBSCRIPTION = 'subscription'
PAYPAL_TRANSACTION_PRICE = 0.45

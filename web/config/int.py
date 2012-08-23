
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django_cassandra.db', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.                                                     
        'NAME': 'knotis', # Or path to database file if using sqlite3.                                                                                                  
        'USER': '', # Not used with sqlite3.                                                                                                                            
        'PASSWORD': '', # Not used with sqlite3.                                                                                                                        
        'HOST': '74.121.189.154', # Set to empty string for localhost. Not used with sqlite3.                                                                           
        'PORT': '5551', # Set to empty string for default. Not used with sqlite3.                                                                                       
    }
}

EMAIL_HOST_USER = 'support.int.knotis@gmail.com'
EMAIL_HOST_PASSWORD = 'wheeling and dealing'

# Base url for external access
BASE_URL = 'wow3.knotis.com' # NO TRAILING SLASH!!!

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
STATIC_URL_ABSOLUTE = BASE_URL + STATIC_URL

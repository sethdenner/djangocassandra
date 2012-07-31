import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'venv/lib/python2.7/site-packages/')))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'web')))
sys.path.insert(0, os.path.abspath(os.path.join(root_path, 'web', 'app')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

from django.contrib import admin

from util import get_quick_models

for m in get_quick_models():
    #print "registering admin for:" + str(m)
    admin.site.register(m)

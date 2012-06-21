from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    pass
from models.users import UserProfile
from models.notifications import NotificationPreferences
admin.site.register(UserProfile, UserAdmin)
admin.site.register(NotificationPreferences, UserAdmin)

class EndpointAdmin(admin.ModelAdmin):
    pass
from models.types import EndpointType
from models.endpoints import Endpoint
admin.site.register(EndpointType, EndpointAdmin)
admin.site.register(Endpoint, EndpointAdmin)

class OAuthAdmin(admin.ModelAdmin):
    pass
from piston.models import Consumer
admin.site.register(Consumer, OAuthAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('value', 'c_type', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['value']
    pass

from models.contents import Content, ContentType
admin.site.register(Content, ContentAdmin)

class ContentTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContentType, ContentTypeAdmin)



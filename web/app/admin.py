from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    pass
from models.user import UserProfile
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

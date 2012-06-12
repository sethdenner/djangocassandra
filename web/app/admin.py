from django.contrib import admin

class AccountsAdmin(admin.ModelAdmin):
    pass
from models.knotis.accounts import Currency, AccountType, Account 
admin.site.register(Currency, AccountsAdmin);
admin.site.register(AccountType, AccountsAdmin);
admin.site.register(Account, AccountsAdmin);

class BusinessesAdmin(admin.ModelAdmin):
    pass
from models.knotis.businesses import Business
admin.site.register(Business, BusinessesAdmin)


class UserAdmin(admin.ModelAdmin):
    pass
from models.knotis.user import UserProfile
admin.site.register(UserProfile, UserAdmin)

class EndpointAdmin(admin.ModelAdmin):
    pass
from models.knotis.types import EndpointType
from models.knotis.endpoints import Endpoint
admin.site.register(EndpointType, EndpointAdmin)
admin.site.register(Endpoint, EndpointAdmin)

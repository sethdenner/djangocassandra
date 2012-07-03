from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    pass
from models.users import UserProfile
from models.notifications import NotificationPreferences
admin.site.register(UserProfile, UserAdmin)
admin.site.register(NotificationPreferences, UserAdmin)


class EndpointAdmin(admin.ModelAdmin):
    pass
from models.endpoints import Endpoint, EndpointType
admin.site.register(EndpointType, EndpointAdmin)
admin.site.register(Endpoint, EndpointAdmin)


class OAuthAdmin(admin.ModelAdmin):
    pass
from piston.models import Consumer
admin.site.register(Consumer, OAuthAdmin)


from models.contents import Content, ContentType
class ContentAdmin(admin.ModelAdmin):
    list_display = ('value', 'c_type', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['value']
    pass

admin.site.register(Content, ContentAdmin)

class ContentTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContentType, ContentTypeAdmin)

from models.businesses import Business, BusinessEndpoint
from models.establishments import Establishment, EstablishmentEndpoint, EstablishmentHours
from models.user_relations import UserRelation, UserRelationType, UserRelationEndpoint
from models.accounts import Account, AccountType, Currency
from models.purchases import Purchase, PurchaseType
from models.products import Product
from models.actions import Action, ActionType

class GeneralAdmin(admin.ModelAdmin):
    pass
admin.site.register(Business, GeneralAdmin)
admin.site.register(BusinessEndpoint, GeneralAdmin)

admin.site.register(UserRelation, GeneralAdmin)
admin.site.register(UserRelationType, GeneralAdmin)
admin.site.register(UserRelationEndpoint, GeneralAdmin)

admin.site.register(Account, GeneralAdmin)
admin.site.register(AccountType, GeneralAdmin)
admin.site.register(Currency, GeneralAdmin)

admin.site.register(Purchase, GeneralAdmin)
admin.site.register(PurchaseType, GeneralAdmin)
admin.site.register(Product, GeneralAdmin)

admin.site.register(Action, GeneralAdmin)
admin.site.register(ActionType, GeneralAdmin)

admin.site.register(Establishment, GeneralAdmin)
admin.site.register(EstablishmentEndpoint, GeneralAdmin)
admin.site.register(EstablishmentHours, GeneralAdmin)


#class TestModelAdmin(admin.ModelAdmin):
#    pass
#from models.testmodel import TestModel
#admin.site.register(TestModel, TestModelAdmin)

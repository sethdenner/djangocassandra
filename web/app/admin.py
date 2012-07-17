from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    pass
from models.users import UserProfile
admin.site.register(UserProfile, UserAdmin)

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
    list_display = ('value', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['value']
    pass

admin.site.register(ContentType, ContentTypeAdmin)

from models.businesses import Business, BusinessEndpoint
from models.establishments import Establishment, EstablishmentEndpoint, EstablishmentHours
from models.user_relations import UserRelation, UserRelationType, UserRelationEndpoint
from models.accounts import Account, AccountType, Currency
from models.purchases import Purchase, PurchaseType
from models.products import Product
from models.offers import Offer, OfferType, OfferProducts, OfferInventory
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

admin.site.register(Offer, GeneralAdmin)
admin.site.register(OfferType, GeneralAdmin)
admin.site.register(OfferProducts, GeneralAdmin)
admin.site.register(OfferInventory, GeneralAdmin)

admin.site.register(Action, GeneralAdmin)
admin.site.register(ActionType, GeneralAdmin)

admin.site.register(Establishment, GeneralAdmin)
admin.site.register(EstablishmentEndpoint, GeneralAdmin)
admin.site.register(EstablishmentHours, GeneralAdmin)

from djangotoolbox.fields import EmbeddedModelField
from django.forms import ModelChoiceField, ModelForm
from models.testmodel import TestModel, EmbeddedModelFieldTest
class EmbeddedModelFieldTestAdminForm(ModelForm, object):
    class Meta:
        model = EmbeddedModelFieldTest
    
    embedded = ModelChoiceField(queryset=TestModel.objects)
    def __init__(self, *args, **kwargs):
        super(EmbeddedModelFieldTestAdminForm, self).__init__(*args, **kwargs)
        
        # self.fields['embedded'] = ModelChoiceField(queryset=TestModel.objects)

class EmbeddedModelFieldTestAdmin(admin.ModelAdmin):
    form = EmbeddedModelFieldTestAdminForm
admin.site.register(EmbeddedModelFieldTest, EmbeddedModelFieldTestAdmin)
    
class TestModelAdmin(admin.ModelAdmin):
    pass
admin.site.register(TestModel, TestModelAdmin)

#class TestModelAdmin(admin.ModelAdmin):
#    pass
#from models.testmodel import TestModel
#admin.site.register(TestModel, TestModelAdmin)

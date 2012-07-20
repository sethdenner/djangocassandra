from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm
from models.accounts import Account, AccountType, Currency
from models.actions import Action, ActionType
from models.businesses import Business, BusinessEndpoint
from models.contents import Content, ContentType
from models.endpoints import Endpoint, EndpointType
from models.establishments import Establishment, EstablishmentEndpoint, \
    EstablishmentHours
from models.offers import Offer, OfferType, OfferProducts, OfferInventory
from models.products import Product
from models.purchases import Purchase, PurchaseType
from models.testmodel import TestModel, EmbeddedModelFieldTest
from models.user_relations import UserRelation, UserRelationType, \
    UserRelationEndpoint
from models.users import UserProfile
from piston.models import Consumer


class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserAdmin)


class EndpointAdmin(admin.ModelAdmin):
    pass
admin.site.register(EndpointType, EndpointAdmin)
admin.site.register(Endpoint, EndpointAdmin)


class OAuthAdmin(admin.ModelAdmin):
    pass
admin.site.register(Consumer, OAuthAdmin)


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


class BusinessForm(ModelForm):
    class Meta:
        model = Business

    def __init__(self, *args, **kwargs):
        super(BusinessForm, self).__init__(*args, **kwargs)

        self.fields['content'].widget.choices = \
            [(i.pk, i) for i in Content.objects.all()]

        if self.instance.pk:
            self.fields['content'].initial = self.instance.content


class BusinessAdmin(admin.ModelAdmin):
    form = BusinessForm

    def __init__(self, model, admin_site):
        super(BusinessAdmin, self).__init__(model, admin_site)
admin.site.register(Business, BusinessAdmin)


class GeneralAdmin(admin.ModelAdmin):
    pass
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

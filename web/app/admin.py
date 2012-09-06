from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm
from models.accounts import Account, AccountType, Currency
from models.actions import Action, ActionType
from models.businesses import Business
from models.contents import Content
from models.endpoints import Endpoint
from models.establishments import Establishment, EstablishmentEndpoint, \
    EstablishmentHours
from models.offers import Offer
from models.products import Product
from models.purchases import Purchase, PurchaseType
from models.testmodel import TestModel, EmbeddedModelFieldTest
from models.user_relations import UserRelation, UserRelationType, \
    UserRelationEndpoint
from models.images import Image
from models.users import UserProfile
from piston.models import Consumer


class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserAdmin)


class EndpointAdmin(admin.ModelAdmin):
    pass
admin.site.register(Endpoint, EndpointAdmin)


class OAuthAdmin(admin.ModelAdmin):
    pass
admin.site.register(Consumer, OAuthAdmin)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'parent', 'content_type', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['value']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['initial'] = request.user.id
            return db_field.formfield(**kwargs)
        return super(ContentAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

admin.site.register(Content, ContentAdmin)


class BusinessForm(ModelForm):
    class Meta:
        model = Business

    def __init__(self, *args, **kwargs):
        super(BusinessForm, self).__init__(*args, **kwargs)

        """
        self.fields['root_content'].widget.choices = \
            [(i.pk, i) for i in Content.objects.all()]

        if self.instance.pk:
            self.fields['root_content'].initial = self.instance.content
        """

class BusinessAdmin(admin.ModelAdmin):
    form = BusinessForm

    def __init__(self, model, admin_site):
        super(BusinessAdmin, self).__init__(model, admin_site)
admin.site.register(Business, BusinessAdmin)


class GeneralAdmin(admin.ModelAdmin):
    pass

admin.site.register(Image, GeneralAdmin)
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

from django.contrib import admin
from django.contrib import contenttypes
from django.forms import ModelForm

from knotis_auth.models import User, UserProfile
from knotis_contact.models import Contact

from models.businesses import Business, BusinessLink, BusinessSubscription
from models.contents import Content
from models.endpoints import Endpoint
from models.offers import Offer
from models.media import Image
from models.cities import City
from models.neighborhoods import Neighborhood
from models.categories import Category
from models.transactions import Transaction
from knotis_qrcodes.models import Qrcode, Scan

from piston.models import Consumer


class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)

class UserAdmin(admin.ModelAdmin):
    search_fields = ['username']
admin.site.register(User, UserAdmin)

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
    search_fields = ['backend_name']

    def __init__(self, model, admin_site):
        super(BusinessAdmin, self).__init__(model, admin_site)

admin.site.register(Business, BusinessAdmin)

class ImageAdmin(admin.ModelAdmin):
    search_fields = ['related_object_id']
admin.site.register(Image, ImageAdmin)


class GeneralAdmin(admin.ModelAdmin):
    pass
admin.site.register(Contact, GeneralAdmin)
admin.site.register(contenttypes.models.ContentType, GeneralAdmin)
admin.site.register(BusinessLink, GeneralAdmin)
admin.site.register(BusinessSubscription, GeneralAdmin)
admin.site.register(Scan, GeneralAdmin)
admin.site.register(Qrcode, GeneralAdmin)
admin.site.register(Transaction, GeneralAdmin)
admin.site.register(City, GeneralAdmin)
admin.site.register(Neighborhood, GeneralAdmin)
admin.site.register(Category, GeneralAdmin)
admin.site.register(Offer, GeneralAdmin)

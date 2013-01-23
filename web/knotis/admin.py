from django.contrib import admin
from django.contrib import contenttypes
from django.forms import ModelForm

from knotis.contrib.auth.models import (
    KnotisUser,
    UserProfile
)
from knotis.contrib.content.models import Content
from knotis.contrib.business.models import (
    Business,
    BusinessLink,
    BusinessSubscription
)
from knotis.contrib.endpoint.models import Endpoint
from knotis.contrib.offer.models import Offer
from knotis.contrib.media.models import Image
from knotis.contrib.category.models import (
    Category,
    City,
    Neighborhood
)
from knotis.contrib.transaction.models import Transaction
from knotis.contrib.qrcode.models import (
    Qrcode,
    Scan
)
from knotis.contrib.contact.models import Contact


class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username']
admin.site.register(KnotisUser, UserAdmin)


class EndpointAdmin(admin.ModelAdmin):
    pass
admin.site.register(Endpoint, EndpointAdmin)


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


class TransactionAdmin(admin.ModelAdmin):
    search_fields = [
        'transaction_context'
    ]
admin.site.register(Transaction, TransactionAdmin)


class GeneralAdmin(admin.ModelAdmin):
    pass
admin.site.register(Contact, GeneralAdmin)
admin.site.register(contenttypes.models.ContentType, GeneralAdmin)
admin.site.register(BusinessLink, GeneralAdmin)
admin.site.register(BusinessSubscription, GeneralAdmin)
admin.site.register(Scan, GeneralAdmin)
admin.site.register(Qrcode, GeneralAdmin)
admin.site.register(City, GeneralAdmin)
admin.site.register(Neighborhood, GeneralAdmin)
admin.site.register(Category, GeneralAdmin)
admin.site.register(Offer, GeneralAdmin)

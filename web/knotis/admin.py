from django.contrib import admin
from django.contrib import contenttypes

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.endpoint.models import Endpoint
from knotis.contrib.offer.models import Offer
from knotis.contrib.media.models import Image
from knotis.contrib.transaction.models import Transaction
from knotis.contrib.qrcode.models import (
    Qrcode,
    Scan
)


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username']
admin.site.register(KnotisUser, UserAdmin)


class EndpointAdmin(admin.ModelAdmin):
    pass
admin.site.register(Endpoint, EndpointAdmin)


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
admin.site.register(contenttypes.models.ContentType, GeneralAdmin)
admin.site.register(Scan, GeneralAdmin)
admin.site.register(Qrcode, GeneralAdmin)
admin.site.register(Offer, GeneralAdmin)

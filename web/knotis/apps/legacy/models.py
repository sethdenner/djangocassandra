from django.db.models import (
    Model,
    IntegerField
)

from knotis.apps.business.models import Business
from knotis.apps.offer.models import Offer
from knotis.apps.auth.models import KnotisUser
from knotis.apps.qrcode.models import Qrcode
from knotis.apps.cassandra.models import ForeignKey


class BusinessIdMap(Model):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_business = ForeignKey(Business)


class OfferIdMap(Model):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_offer = ForeignKey(Offer)


class UserIdMap(Model):
    old_id = IntegerField(
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    new_user = ForeignKey(KnotisUser)


class QrcodeIdMap(Model):
    old_id = IntegerField(
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    new_qrcode = ForeignKey(Qrcode)

from django.db.models import (
    Model,
    IntegerField
)

from knotis.contrib.business.models import Business
from knotis.contrib.offer.models import Offer
from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.qrcode.models import Qrcode
from knotis.contrib.cassandra.models import ForeignKey
from knotis.contrib.core.models import KnotisModel


class BusinessIdMap(KnotisModel):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_business = ForeignKey(Business)


class OfferIdMap(KnotisModel):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_offer = ForeignKey(Offer)


class UserIdMap(KnotisModel):
    old_id = IntegerField(
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    new_user = ForeignKey(KnotisUser)


class QrcodeIdMap(KnotisModel):
    old_id = IntegerField(
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    new_qrcode = ForeignKey(Qrcode)

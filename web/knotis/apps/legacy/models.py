from django.db.models import (
    Model,
    IntegerField
)

from knotis.apps.business.models import Business
from knotis.apps.offer.models import Offer
from knotis.apps.auth.models import KnotisUser
from knotis.apps.qrcode.models import Qrcode
from knotis.apps.cassandra.models import ForeignKey
from knotis.apps.core.models import KnotisModel


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

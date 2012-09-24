from django.db.models import Model, IntegerField
from app.models.businesses import Business
from app.models.offers import Offer
from knotis_auth.models import User
from foreignkeynonrel.models import ForeignKeyNonRel


class BusinessIdMap(Model):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_business = ForeignKeyNonRel(Business)


class OfferIdMap(Model):
    old_id = IntegerField(null=True, blank=True, default=None, db_index=True)
    new_offer = ForeignKeyNonRel(Offer)


class UserIdMap(Model):
    old_id = IntegerField(
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    new_user = ForeignKeyNonRel(User)
    
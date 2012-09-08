from django.db.models import OneToOneField, FloatField, IntegerField, \
    NullBooleanField
from foreignkeynonrel.models import ForeignKeyNonRel
from django.contrib.auth.models import User

from app.models.knotis import KnotisModel
from app.models.fields.math import MatrixField
from app.models.endpoints import Endpoint


class UserEndpoints(KnotisModel):
    user = ForeignKeyNonRel(User, primary_key=True)
    endpoint = ForeignKeyNonRel(Endpoint)


class UserProfile(KnotisModel):
    ACCOUNT_TYPES = (
        (0, 'User'),
        (1, 'Business - Free'),
        (2, 'Business - Monthly'),
    )

    ACCOUNT_STATUS = (
        (0, 'Disabled'),
        (1, 'Active')
    )

    user = OneToOneField(User, primary_key=True)

    account_type = IntegerField(null=True, choices=ACCOUNT_TYPES, default=0)
    account_status = IntegerField(null=True, choices=ACCOUNT_STATUS, default=0)

    notify_announcements = NullBooleanField(blank=True, default=False)
    notify_offers = NullBooleanField(blank=True, default=False)
    notify_events = NullBooleanField(blank=True, default=False)

    reputation_mu = FloatField(null=True, default='1.0')
    reputation_sigma = FloatField(null=True, default='0.0')
    reputation_total = FloatField(null=True, default='0.0')
    reputation_matrix = MatrixField(null=True, blank=True, max_length=200)

    def is_business_owner(self):
        return True if self.account_type != 0 else False

from django.db.models import OneToOneField, FloatField
from foreignkeynonrel.models import ForeignKeyNonRel
from django.contrib.auth.models import User

from app.models.knotis import KnotisModel
from app.models.fields.math import MatrixField
from app.models.endpoints import Endpoint


class UserEndpoints(KnotisModel):
    user = ForeignKeyNonRel(User, primary_key=True)
    endpoint = ForeignKeyNonRel(Endpoint)


class UserProfile(KnotisModel):
    user = OneToOneField(User, primary_key=True)

    reputation_mu = FloatField(null=True, default='1.0')
    reputation_sigma = FloatField(null=True, default='0.0')
    reputation_total = FloatField(null=True, default='0.0')
    reputation_matrix = MatrixField(null=True, blank=True, max_length=200)

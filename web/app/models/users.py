from django.db.models import ForeignKey, OneToOneField, FloatField
from django.contrib.auth.models import User

from app.models.knotis import KnotisModel
from app.models.notifications import NotificationPreferences
from app.models.fields.math import MatrixField
from app.models.endpoints import Endpoint

class UserEndpoints(KnotisModel):
    user = ForeignKey(User, primary_key=True)
    endpoint = ForeignKey(Endpoint)

class UserProfile(KnotisModel):
    user = OneToOneField(User, primary_key=True)
    notification_preferences = OneToOneField(NotificationPreferences, null=True)

    reputation_avg = FloatField()
    reputation_total = FloatField()
    reputation_matrix = MatrixField()

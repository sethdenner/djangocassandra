from django.db.models import OneToOneField
from django.contrib.auth.models import User
from app.models.knotis import KnotisModel
from app.models.notifications import NotificationPreferences

class UserProfile(KnotisModel):
    user = OneToOneField(User, primary_key=True)
    notification_preferences = OneToOneField(NotificationPreferences)

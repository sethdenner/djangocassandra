from django.db.models import BooleanField, OneToOneField
from django.contrib.auth.models import User
from app.models.knotis import KnotisModel

class NotificationPreferences(KnotisModel):
  class Meta(KnotisModel.Meta):
    verbose_name = "Notification Preferences"
    verbose_name_plural = "Notification Preferences"
    
  user = OneToOneField(User, primary_key=True)
  service_announcements = BooleanField()
  new_deals = BooleanField()
  new_events = BooleanField()

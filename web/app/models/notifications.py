from django.db import models
from web.app.knotis.db import KnotisModel

class NotificationPreferences(KnotisModel):
  service_announcements = models.BooleanField()
  new_deals = models.BooleanField()
  new_events = models.BooleanField()

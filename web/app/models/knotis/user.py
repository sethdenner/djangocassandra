from django.db import models
from django.contrib.auth.models import User
from web.app.knotis.db import KnotisModel

class UserProfile(KnotisModel):
    user = models.OneToOneField(User, primary_key=True)

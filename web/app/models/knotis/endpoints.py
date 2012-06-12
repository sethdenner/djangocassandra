from django.db import models
from django.contrib.auth.models import User
from web.app.knotis.db import KnotisModel
from types import EndpointType

class Endpoint(KnotisModel):
    user = models.ForeignKey(User, primary_key=True)
    type = models.ForeignKey(EndpointType)
    value = models.CharField(max_length=1024)

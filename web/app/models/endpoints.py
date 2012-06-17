from django.db.models import ForeignKey, CharField
from django.contrib.auth.models import User
from app.models.knotis import KnotisModel
from app.models.types import EndpointType

class Endpoint(KnotisModel):
    user = ForeignKey(User)
    type = ForeignKey(EndpointType)
    value = CharField(max_length=1024)

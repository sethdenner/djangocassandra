from django.db import models
from web.app.knotis.db import KnotisModel

from contents import Content
from products import Product
from businesses import Business
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class UserEmail(KnotisModel):
    email = models.CharField(max_length=140)
    priority = models.IntegerField()
    confirmed = models.CharField(max_length=140)
    pub_date = models.DateTimeField('date published') # date created.
    updated_date = models.DateTimeField('date published') # last updated
    state = models.BooleanField() # later an enum for (disabled etc.) Create your models here.

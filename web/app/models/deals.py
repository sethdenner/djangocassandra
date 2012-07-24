from django.db import models
from web.app.knotis.db import KnotisModel

class Deal(KnotisModel):
    Title = models.CharField(max_length=140)
    Description = models.CharField(max_length=2000)
    pub_date = models.DateTimeField('date published')

class Upsell(KnotisModel):
    deal = models.ForeignKeyNonRel(Deal)
    choice = models.CharField(max_length=200)
    clicks = models.IntegerField()
    bounces = models.IntegerField()
# Create your models here.

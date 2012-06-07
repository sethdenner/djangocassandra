from django.db import models

class Deal(models.Model):
    Title = models.CharField(max_length=140)
    Description = models.CharField(max_length=2000)
    pub_date = models.DateTimeField('date published')

class Upsell(models.Model):
    deal = models.ForeignKey(Deal)
    choice = models.CharField(max_length=200)
    clicks = models.IntegerField()
    bounces = models.IntegerField()
# Create your models here.

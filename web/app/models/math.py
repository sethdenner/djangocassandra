from django.db import models
from app.models.knotis import KnotisModel

#from django.contrib.auth.models import User

# this isn't ready at all..
class Countable(KnotisModel):
    parent_id = models.IntegerField()
    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
#    user = models.ForeignKeyNonRel(User)
#    c_parent = models.ForeignKeyNonRel('self')
#    c_type = models.CharField(max_length=140)
#    content = Base64Field()
    pub_date = models.DateTimeField('date published')

#class Content.Type(KnotisModel):
#    deal = models.ForeignKeyNonRel(Deal)
#    choice = models.CharField(max_length=200)
#    clicks = models.IntegerField()
#    bounces = models.IntegerField()

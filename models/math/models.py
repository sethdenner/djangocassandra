from django.db import models
#from django.contrib.auth.models import User

# this isn't ready at all..
class Countable(models.Model):
    parent_id = model.IntField()
    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
#    user = models.ForeignKey(User)
#    c_parent = models.ForeignKey('self')
#    c_type = models.CharField(max_length=140)
#    content = Base64Field()
    pub_date = models.DateTimeField('date published')
    
#class Content.Type(models.Model):
#    deal = models.ForeignKey(Deal)
#    choice = models.CharField(max_length=200)
#    clicks = models.IntegerField()
#    bounces = models.IntegerField()

from django.db import models
from contents.models import Content
#from django.contrib.auth.models import User

# this isn't ready at all..
class Business(models.Model):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
    user = models.ForeignKey(User)
    c_parent = models.ForeignKey(Content)
    b_name = models.CharField(max_length=140)
#    content = Base64Field()
    pub_date = models.DateTimeField('date published')

# FIXME: Implement tag's as content node types submitted by users.  The core tennant of 
#class BusinessTag(models.Model):
#    business = models.ForeignKey(Business)
#    bt_parent = models.ForeignKey(Content)
    
#    choice = models.CharField(max_length=200)
#    clicks = models.IntegerField()
#    bounces = models.IntegerField()# Create your models here. Create your models here.

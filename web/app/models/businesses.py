from django.db import models
from web.app.knotis.db import KnotisModel

from django.contrib.auth.models import User
from contents import Content
#from django.contrib.auth.models import User

class BusinessEndpoinst(KnotisModel):
    business = models.ForeignKey(Business)
    endpoint = models.ForeignKey(Endpoint)

# this isn't ready at all..
class Business(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Business"
        verbose_name_plural = 'Businesses'
        
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
    content_parent = models.ForeignKey(Content)
    name = models.CharField(max_length=140)

    # can be a url or maybe an id for gravatar.
    avatar = models.CharField(max_length=140, null=true)

#    content = Base64Field()
    pub_date = models.DateTimeField('date published')

# FIXME: Implement tag's as content node types submitted by users.  The core tennant of 
#class BusinessTag(KnotisModel):
#    business = models.ForeignKey(Business)
#    bt_parent = models.ForeignKey(Content)
    
#    choice = models.CharField(max_length=200)
#    clicks = models.IntegerField()
#    bounces = models.IntegerField()# Create your models here. Create your models here.

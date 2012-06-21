from django.db import models
from web.app.knotis.db import KnotisModel

from contents import Content
from products import Product
from businesses import Business
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

"""
This class registers subscriptions.

Anytime that any content is updated, logic can be executed or queued for execution to knotify anyone who is subscribed.

"""
class SubscriptionType(KnotisModel):
    name = models.CharField(max_length=140)

class Subscription(KnotisModel):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
# There defidinetyl needs to be a lot more logic going on in here...
    user = models.ForeignKey(User)
    subscriptionttype = models.ForeignKey(SubscriptionType)
    c_parent = models.ForeignKey(Content)
    name = models.CharField(max_length=140) # text the user gives this Subscription? I don't know....
    pub_date = models.DateTimeField('date published') # date created.
    updated_date = models.DateTimeField('date published') # last updated
    state = models.BooleanField() # later an enum for (disabled etc.)

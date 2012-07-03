from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from web.app.knotis.db import KnotisModel
from app.models.fields.permissions import PermissionsField

from contents import Content
#from products import Product
#from businesses import Business

"""

This class registers user relationships with all other types of data..

Anytime that any content is updated, logic can be executed or queued for execution to knotify anyone who is subscribed.


This might be stupid. However, allowing relations between users and relations in a recursive fashion, will allow for concepts like "I'm following my christmas list, my christmas list is following _____".

"""
class UserRelationType(KnotisModel):
    USER_RELATION_TYPES = (
        ('0', 'owner'), # busines
        ('1', 'employee'), # busines
        ('2', 'customer'), # busines
        ('3', '________'), # busines
        ('4', 'category'), # tag
        ('5', 'cart'),     # offer
        ('6', 'purchase'), # purchase
        ('7', 'relation_collection'), #someday maybe there will be a way to drag and drop relations making them organizable.
        ('8', 'product'),   # product
        ('9', 'follow_business'), # busines
        ('10', 'follow_tag'), # busines
        ('11', 'follow_offer'), # offer
        ('12', 'content'), # offer
    )

    value       = CharField(max_length=30, choices=USER_RELATION_TYPES)
    permissions = PermissionsField(Permissions)

    pub_date = models.DateTimeField('date published')
    def __unicode__(self):
        return self.name
    #type = models.ForeginKey(KnotisModel)

class UserRelationEndpoint(KnotisModel):
    user_relation = models.ForeignKey(UserRelation)
    endpoint = models.ForeignKey(Endpoint)
    permissions = models.ForeignKey(Permissions)
    pub_date = models.DateTimeField('date published')

class UserRelation(KnotisModel):
    user = models.ForeignKey(User)
    user_relation_name = models.CharField(max_length=140) # text the user gives this user_relation? I don't know....
    user_relation_type = models.ForeignKey(UserRelationType)
    user_relation_foreign_id = models.CharField(max_length=100) # the id of the foreign relation.

    pub_date = models.DateTimeField('date published') # date created.
    updated_date = models.DateTimeField('date published') # last updated
    state = models.BooleanField() # later an enum for (disabled etc.)

from django.contrib.auth.models import Group, User
from django.db.models import CharField, ForeignKey, DateTimeField, FloatField, BooleanField

from app.models.knotis import KnotisModel
from app.models.fields.permissions import PermissionsField

from contents import Content
from endpoints import Endpoint

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
    permissions = PermissionsField()

    pub_date = DateTimeField('date published')
    def __unicode__(self):
        return self.name
    #type = ForeginKey(KnotisModel)

class UserRelation(KnotisModel):
    user = ForeignKey(User)
    user_relation_name = CharField(max_length=140) # text the user gives this user_relation? I don't know....
    user_relation_type = ForeignKey(UserRelationType)
    user_relation_foreign_id = CharField(max_length=100) # the id of the foreign relation.

    pub_date = DateTimeField('date published') # date created.
    updated_date = DateTimeField('date published') # last updated
    state = BooleanField() # later an enum for (disabled etc.)

class UserRelationEndpoint(KnotisModel):
    user_relation = ForeignKey(UserRelation)
    endpoint = ForeignKey(Endpoint)
    permissions = PermissionsField()
    pub_date = DateTimeField('date published')


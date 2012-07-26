from django.contrib.auth.models import Group, User
from django.db.models import CharField, DateTimeField, FloatField, BooleanField
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField
from app.models.contents import Content
from app.models.endpoints import Endpoint

# from manytomany.models import ManyToManyField
from manytomanynonrel.models import ManyToManyModelField
from django.utils.termcolors import foreground


class Business(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Business"
        verbose_name_plural = 'Businesses'

    content_root = ForeignKeyNonRel(Content, related_name='business_content_root', null=True)
    # content = ManyToManyModelField(ForeignKeyNonRel(Content))
    name = CharField(max_length=140)

    # can be a url or maybe an id for gravatar.
    avatar = ForeignKeyNonRel(Content, related_name='business_avatar', null=True)
    hours = ForeignKeyNonRel(Content, related_name='business_hours', null=True)
    business_name = ForeignKeyNonRel(Content, related_name='business_name', null=True)

    # avatar = CharField(max_length=140, null=True)

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __unicode__(self):
        output_array = [
            self.name,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])

# FIXME: Implement tag's as content node types submitted by users.  The core tennant of 
#class BusinessTag(KnotisModel):
#    business = ForeignKeyNonRel(Business)
#    bt_parent = ForeignKeyNonRel(Content)

#    choice = CharField(max_length=200)
#    clicks = IntegerField()
#    bounces = IntegerField()# Create your models here. Create your models here.

class BusinessEndpoint(KnotisModel):
    business = ForeignKeyNonRel(Business)
    endpoint = ForeignKeyNonRel(Endpoint)


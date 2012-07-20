from django.contrib.auth.models import Group, User
from django.db.models import CharField, ForeignKey, DateTimeField, FloatField, BooleanField

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField
from app.models.contents import Content
from app.models.endpoints import Endpoint

# from manytomany.models import ManyToManyField
from manytomanynonrel.models import ManyToManyModelField


class Business(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Business"
        verbose_name_plural = 'Businesses'

#    parent_id = model.IntField()
#    parent_type = CharField(max_length=200) # probably a stupid way to do this.
#    content = ForeignKey(Content)
    content = ManyToManyModelField(ForeignKey(Content))
    name = CharField(max_length=140)

    # can be a url or maybe an id for gravatar.
    avatar = CharField(max_length=140, null=True)

#    content = Base64Field()
    pub_date = DateTimeField('date published')

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
#    business = ForeignKey(Business)
#    bt_parent = ForeignKey(Content)
    
#    choice = CharField(max_length=200)
#    clicks = IntegerField()
#    bounces = IntegerField()# Create your models here. Create your models here.

class BusinessEndpoint(KnotisModel):
    business = ForeignKey(Business)
    endpoint = ForeignKey(Endpoint)


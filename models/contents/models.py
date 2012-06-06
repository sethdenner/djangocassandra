from django.db import models
#from django.db.models import User
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

#---------- Move to separate file.
import base64
#from django.db import models


class Base64Field(models.TextField):

    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))

# ------ End Base64Field

class ContentType(models.Model):
    name  = models.CharField(max_length=200)
    user    = models.ForeignKey(User)
    group    = models.ForeignKey(Group)
    instances  = models.IntegerField()
    pub_date = models.DateTimeField('date published')
    def __unicode__(self):
        return self.name

class Content(models.Model):
#    FIXME: how do we make this auto version so that save actually just increments a version to the list but we always have old versions?
#    cid = content id.
#    parent_id(indexed)
#    owner_id(indexed)
#    type_id
#    content=(text or value)
#    created_time
#    certainty=(mu,sigma)
    user = models.ForeignKey(User)
    group    = models.ForeignKey(Group)
    c_parent = models.ForeignKey('self')
    c_type = models.ForeignKey(ContentType)
    value = models.CharField(max_length=2000) #Base64Field()
    certanty_mu = models.FloatField() # average - expected value
    certanty_sigma = models.FloatField() # stdev - expected error
    pub_date = models.DateTimeField('date published')
    
    def __unicode__(self):
        return self.value

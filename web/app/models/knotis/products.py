from django.db import models
from web.app.knotis.db import KnotisModel

from contents import Content
#from django.contrib.auth.models import User

# this isn't ready at all..
class Product(KnotisModel):
#    parent_id = model.IntField()
#    parent_type = models.CharField(max_length=200) # probably a stupid way to do this.
#    user = models.ForeignKey(User)
#    c_parent = models.ForeignKey('self')
#    c_type = models.CharField(max_length=140)
#    content = Base64Field()
    pub_date = models.DateTimeField('date published')
    
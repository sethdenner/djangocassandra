from django.contrib.auth.models import User, Group
from django.db.models import CharField, ForeignKey, DateTimeField, FloatField

from app.models.knotis import KnotisModel
from app.models.fields.binary import Base64Field
from app.models.fields.permissions import PermissionsField


class ContentType(KnotisModel):
    CONTENT_TYPES = (
        ('0', 'root'),
        ('1', 'site text'),
        ('2', 'user submitted')
        # terms of service
        # hours, address, business name, all endpoints, anything that a user can say about a business.
    )

    value       = CharField(max_length=30, choices=CONTENT_TYPES)
    permissions = PermissionsField()

    pub_date = DateTimeField('date published')
    def __unicode__(self):
        return self.value

class Content(KnotisModel):
#    FIXME: how do we make this auto version so that save actually just increments a version to the list but we always have old versions?
#    cid = content id.
#    parent_id(indexed)
#    owner_id(indexed)
#    type_id
#    content=(text or value)
#    created_time
#    certainty=(mu,sigma)

    user = ForeignKey(User)
    group = ForeignKey(Group, null=True)
    permissions = PermissionsField()

    c_parent = ForeignKey('self')
    #content_parent = ForeignKey('self')
    #content_previous = ForeignKey('self')

    c_type = ForeignKey(ContentType)
    value = CharField(max_length=2000) #Base64Field()

    certanty_mu = FloatField() # average - expected value
    certanty_sigma = FloatField() # stdev - expected error

    pub_date = DateTimeField('date published')
    
    def __unicode__(self):
        return self.value

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


from django.contrib.auth.models import User, Group
from django.db.models import CharField, DateTimeField, FloatField
from foreignkeynonrel.models import ForeignKeyNonRel
from django.utils.datetime_safe import datetime

from app.models.knotis import KnotisModel


class Content(KnotisModel):
#    FIXME: how do we make this auto version so that save actually just
#    increments a version to the list but we always have old versions?
#    cid = content id.
#    parent_id(indexed)
#    owner_id(indexed)
#    type_id
#    content=(text or value)
#    created_time
#    certainty=(mu,sigma)
    CONTENT_TYPES = (
        ('0', 'Root'),
        ('1', 'Site Text'),
        ('2', 'User Submitted'),
        ('3.0', 'Business Root'),
        ('3.1', 'Business Name'),
        ('3.2', 'Business Hours'),
        ('3.3', 'Business Avatar'),
        ('3.4', 'Business Summary'),
        ('3.5', 'Business Description'),
        ('3.6', 'Business Short Name'),
        ('4', 'Endpoint'),
        ('4.1', 'Endpoint Email'),
        ('4.2', 'Endpoint Phone'),
        ('4.3', 'Endpoint Address'),
        ('4.4', 'Endpoint Twitter')

        # terms of service
        # hours, address, business name, all endpoints, anything that a user
        # can say about a business.
    )

    LOCALES = (
        ('en_us', 'en_us'),
        ('jp', 'jp')
    )

    content_type = CharField(max_length=30, choices=CONTENT_TYPES, null=True)
    locale = CharField(max_length='10', choices=LOCALES, null=True, default=LOCALES[0])

    user = ForeignKeyNonRel(User,)
    group = ForeignKeyNonRel(Group, null=True, blank=True)
    #permissions = ManyToManyField(Permission, null=True, blank=True)
    #permission = ForeignKeyNonRel(Permission, null=True, blank=True)
    #permissions = PermissionsField()

    parent = ForeignKeyNonRel('self', blank=True, null=True, related_name='content_parent')
    previous = ForeignKeyNonRel('self', related_name='content_previous', blank=True, null=True)

    value = CharField(max_length=2000)  # Base64Field()

    certanty_mu = FloatField()  # average - expected value
    certanty_sigma = FloatField()  # stdev - expected error

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __unicode__(self):
        return self.value

    def was_published_recently(self):
        return self.pub_date >= datetime.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

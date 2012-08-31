from django.contrib.auth.models import User, Group
from django.db.models import CharField, DateTimeField, FloatField, Manager
from foreignkeynonrel.models import ForeignKeyNonRel
from django.utils.datetime_safe import datetime

from app.models.knotis import KnotisModel


class ContentManager(Manager):
    def get_template_content(self, template_name):
        """
        FIXME: Inefficient. We should find some way to reduce this to one
        query instead of 2 through denormalization.
        """ 
        qset = super(ContentManager, self).get_query_set().filter(content_type='1.1').filter(name=template_name)
        parent = qset[0] 
        return super(ContentManager, self).get_query_set().filter(parent=parent)


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
        ('1.0', 'Site Root'),
        ('1.1', 'Template'),
        ('1.2', 'Text'),
        ('1.3', 'URI'),
        ('1.4', 'HTML'),
        ('2.0', 'User Submitted'),
        ('3.0', 'Business Root'),
        ('3.1', 'Business Name'),
        ('3.2', 'Business Summary'),
        ('3.3', 'Business Description'),
        ('4.0', 'Endpoint'),
        ('4.1', 'Endpoint Email'),
        ('4.2', 'Endpoint Phone'),
        ('4.3', 'Endpoint Address'),
        ('4.4', 'Endpoint Twitter'),
        ('4.5', 'Endpoint Facebook'),
        ('4.6', 'Endpoint Yelp')

        # terms of service
        # hours, address, business name, all endpoints, anything that a user
        # can say about a business.
    )

    LOCALES = (
        ('en_us', 'en_us'),
        ('jp', 'jp')
    )

    content_type = CharField(max_length=30, choices=CONTENT_TYPES, null=True, db_index=True)
    locale = CharField(max_length=10, choices=LOCALES, null=True, default=LOCALES[0])
    name = CharField(max_length=30, null=True, db_index=True)

    user = ForeignKeyNonRel(User)
    group = ForeignKeyNonRel(Group, null=True, blank=True, default=None)
    #permissions = ManyToManyField(Permission, null=True, blank=True)
    #permission = ForeignKeyNonRel(Permission, null=True, blank=True)
    #permissions = PermissionsField()

    parent = ForeignKeyNonRel('self', blank=True, null=True, related_name='content_parent', default=None)
    previous = ForeignKeyNonRel('self', related_name='content_previous', blank=True, null=True, default=None)

    value = CharField(max_length=2000, null=True, blank=True, default=None)  # Base64Field()

    certainty_mu = FloatField(null=True, default='1.0')  # average - expected value
    certainty_sigma = FloatField(null=True, default='0.0')  # stdev - expected error

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __unicode__(self):
        if not self.name:
            return '(' + self.id + ')'
        else:
            return self.name + ' (' + self.id + ')'

    def was_published_recently(self):
        return self.pub_date >= datetime.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    
    objects = Manager()
    content_objects = ContentManager()

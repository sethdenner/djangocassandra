from django.contrib.auth.models import User, Group
from django.db.models import CharField, DateTimeField, FloatField, Manager
from foreignkeynonrel.models import ForeignKeyNonRel
from django.utils.datetime_safe import datetime
from django.utils.http import urlquote

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

    def create_content(self):
        pass

class ContentTypes:
    ROOT = 0.
    SITE_ROOT = 1.0
    TEMPLATE = 1.1
    TEXT = 1.2
    URI = 1.3
    HTML = 1.4
    USER_SUBMITTED = 2.
    BUSINESS_ROOT = 3.
    BUSINESS_NAME = 3.1
    BUSINESS_SUMMARY = 3.2
    BUSINESS_DESCRIPTION = 3.3
    ENDPOINT = 4.
    ENDPOINT_EMAIL = 4.1
    ENDPOINT_PHONE = 4.2
    ENDPOINT_ADDRESS = 4.3
    ENDPOINT_TWITTER = 4.4
    ENDPOINT_FACEBOOK = 4.5
    ENDPOINT_YELP = 4.6
    CATEGORY = 5.
    CATEGORY_NAME = 5.1
    CITY = 6.
    CITY_NAME = 6.1
    NEIGHBORHOOD = 7.
    NEIGHBORHOOD_NAME = 7.1
    OFFER = 8.
    OFFER_TITLE = 8.1
    OFFER_DESCRIPTION = 8.2
    OFFER_RESTRICTIONS = 8.3
    IMAGE = 9.
    IMAGE_CAPTION = 9.1

    CHOICES = (
        (ROOT, 'Root'),
        (SITE_ROOT, 'Site Root'),
        (TEMPLATE, 'Template'),
        (TEXT, 'Text'),
        (URI, 'URI'),
        (HTML, 'HTML'),
        (USER_SUBMITTED, 'User Submitted'),
        (BUSINESS_ROOT, 'Business Root'),
        (BUSINESS_NAME, 'Business Name'),
        (BUSINESS_SUMMARY, 'Business Summary'),
        (BUSINESS_DESCRIPTION, 'Business Description'),
        (ENDPOINT, 'Endpoint'),
        (ENDPOINT_EMAIL, 'Endpoint Email'),
        (ENDPOINT_PHONE, 'Endpoint Phone'),
        (ENDPOINT_ADDRESS, 'Endpoint Address'),
        (ENDPOINT_TWITTER, 'Endpoint Twitter'),
        (ENDPOINT_FACEBOOK, 'Endpoint Facebook'),
        (ENDPOINT_YELP, 'Endpoint Yelp'),
        (CATEGORY, 'Category'),
        (CATEGORY_NAME, 'Category Name'),
        (CITY, 'City'),
        (CITY_NAME, 'City Name'),
        (NEIGHBORHOOD, 'Neighborhood'),
        (NEIGHBORHOOD_NAME, 'Neighborhood Name'),
        (OFFER, 'Offer'),
        (OFFER_TITLE, 'Offer Title'),
        (OFFER_DESCRIPTION, 'Offer Description'),
        (OFFER_RESTRICTIONS, 'Offer Restrictions'),
        (IMAGE, 'Image'),
        (IMAGE_CAPTION, 'Image Caption'),
    )

class ContentLocales:
    EN_US = 'en_us'
    JP = 'jp'

    CHOICES = (
        (EN_US, 'en_us'),
        (JP, 'jp')
    )

class Content(KnotisModel):
    user = ForeignKeyNonRel(User)
    group = ForeignKeyNonRel(Group, null=True, blank=True, default=None)

    content_type = FloatField(choices=ContentTypes.CHOICES, blank=True, null=True, db_index=True)
    locale = CharField(max_length=10, choices=ContentLocales.CHOICES, null=True, default=ContentLocales.EN_US)
    name = CharField(max_length=30, null=True, default=None, db_index=True)
    parent = ForeignKeyNonRel('self', blank=True, null=True, related_name='content_parent', default=None)
    previous = ForeignKeyNonRel('self', related_name='content_previous', blank=True, null=True, default=None)
    value = CharField(max_length=2000, null=True, blank=True, default=None)  # Base64Field()

    certainty_mu = FloatField(null=True, default='1.0')  # average - expected value
    certainty_sigma = FloatField(null=True, default='0.0')  # stdev - expected error

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __init__(self, *args, **kwargs):
        name_param = kwargs.get('name')
        if not name_param:
            value_param = kwargs.get('value')
            if value_param:
                kwargs['name'] = urlquote(value_param.strip().lower().replace(' ', '_'))

        super(Content, self).__init__(*args, **kwargs)

    def __unicode__(self):
        if not self.name:
            return '(' + self.id + ')'
        else:
            return self.name + ' (' + self.id + ')'

    def update(
        self,
        value,
        user=None,
        locale=None
    ):
        if not user:
            user = self.user

        if not locale:
            locale = self.locale

        next_content = Content.objects.create(
            user=user,
            content_type=self.content_type,
            locale=locale,
            name=self.name,
            parent=self.parent,
            previous=self,
            value=value
        )

        self.parent = next_content
        self.save()

        return next_content

    def was_published_recently(self):
        return self.pub_date >= datetime.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    objects = ContentManager()

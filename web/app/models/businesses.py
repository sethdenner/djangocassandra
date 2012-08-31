from django.db.models import CharField, DateTimeField
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField
from app.models.contents import Content
from app.models.endpoints import Endpoint


class Business(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Business"
        verbose_name_plural = 'Businesses'

    content_root = ForeignKeyNonRel(Content, related_name='business_content_root', null=True)
    # content = ManyToManyModelField(ForeignKeyNonRel(Content))
    name = CharField(max_length=140)

    # can be a url or maybe an id for gravatar.
    avatar = ForeignKeyNonRel(Content, related_name='business_avatar', null=True, blank=True)
    hours = ForeignKeyNonRel(Content, related_name='business_hours', null=True, blank=True)
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
    
    @staticmethod
    def create_business(
        user,
        backend_name=None,
        business_name=None,
        avatar=None,
        hours=None
    ):
        # Create the root content node for the business.
        content_business_root = Content(
            content_type='3.0',
            locale='en_us',
            user=user,
            group=None,
            parent=None,
            previous=None,
            value=None,
            certainty_mu=1., # Root certainty should always be 100%
            certainty_sigma=0.
        )
        content_business_root.save()

        content_business_name = Content(
            content_type='3.1',
            locale='en_us',
            user=user,
            group=None,
            parent=content_business_root,
            previous=None,
            value=business_name,
            certainty_mu=1., # Derive this from the user eventually
            certainty_sigma=0.
        )
        content_business_name.save()

        content_hours = Content(
            content_type='3.2',
            locale='en_us',
            user=user,
            group=None,
            parent=content_business_root,
            previous=None,
            value=hours,
            certainty_mu=1., # Derive this from the user eventually
            certainty_sigma=0.
        )
        content_hours.save()

        content_avatar = Content(
            content_type='3.3',
            locale='en_us',
            user=user,
            group=None,
            parent=content_business_root,
            previous=None,
            value=avatar,
            certainty_mu=1., # Derive this from the user eventually
            certainty_sigma=0.
        )
        content_avatar.save()

        """
        Now that the content tree for this business
        is built we can create the actual business.
        """
        new_business = Business(
            content_root=content_business_root,
            name=backend_name,
            avatar=content_avatar,
            hours=content_hours,
            business_name=content_business_name
        )
        new_business.save()

        return new_business

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


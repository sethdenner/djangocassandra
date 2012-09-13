from django.db.models import CharField, DateTimeField, URLField, Manager, \
    NullBooleanField
from django.utils.http import urlquote

from foreignkeynonrel.models import ForeignKeyNonRel

from knotis_auth.models import User

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField
from app.models.contents import Content, ContentTypes
from app.models.endpoints import EndpointPhone, EndpointAddress, \
    EndpointTwitter, EndpointFacebook, EndpointYelp
from app.models.media import Image


class BusinessManager(Manager):
    def create_business(
        self,
        user,
        name,
        summary,
        description,
        address,
        phone,
        twitter_name,
        facebook_uri,
        yelp_id
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))

        content_root = Content.objects.create(
            content_type=ContentTypes.BUSINESS_ROOT,
            user=user,
            name=backend_name
        )

        content_business_name = Content.objects.create(
            content_type=ContentTypes.BUSINESS_NAME,
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )

        content_summary = None
        if summary:
            content_summary = Content.objects.create(
                content_type=ContentTypes.BUSINESS_SUMMARY,
                user=user,
                name=backend_name + '_summary',
                parent=content_root,
                value=summary
            )

        content_description = None
        if description:
            content_description = Content.objects.create(
                content_type=ContentTypes.BUSINESS_DESCRIPTION,
                user=user,
                name=backend_name + '_description',
                parent=content_root,
                value=description
            )

        endpoint_address = None
        if address:
            endpoint_address = EndpointAddress.objects.create(
                user=user,
                value=address
            )

        endpoint_phone = None
        if phone:
            endpoint_phone = EndpointPhone.objects.create(
                user=user,
                value=phone
            )

        endpoint_twitter = None
        if twitter_name:
            endpoint_twitter = EndpointTwitter.objects.create(
                user=user,
                value=twitter_name
            )

        endpoint_facebook = None
        if facebook_uri:
            endpoint_facebook = EndpointFacebook.objects.create(
                user=user,
                value=facebook_uri
            )

        endpoint_yelp = None
        if yelp_id:
            endpoint_yelp = EndpointYelp.objects.create(
                user=user,
                value=yelp_id
            )

        business = Business.objects.create(
            user=user,
            backend_name=backend_name,
            content_root=content_root,
            business_name=content_business_name,
            summary=content_summary,
            description=content_description,
            address=endpoint_address,
            phone=endpoint_phone,
            twitter_name=endpoint_twitter,
            facebook_uri=endpoint_facebook,
            yelp_id=endpoint_yelp
        )

        return business


class Business(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Business"
        verbose_name_plural = 'Businesses'

    backend_name = CharField(max_length=128, db_index=True)

    user = ForeignKeyNonRel(User)
    content_root = ForeignKeyNonRel(Content, related_name='business_content_root')
    business_name = ForeignKeyNonRel(Content, related_name='business_business_name')
    summary = ForeignKeyNonRel(Content, related_name='business_summary')
    description = ForeignKeyNonRel(Content, related_name='business_description')

    address = ForeignKeyNonRel(EndpointAddress)
    phone = ForeignKeyNonRel(EndpointPhone)

    twitter_name = ForeignKeyNonRel(EndpointTwitter)
    facebook_uri = ForeignKeyNonRel(EndpointFacebook)
    yelp_id = ForeignKeyNonRel(EndpointYelp)

    primary_image = ForeignKeyNonRel(Image)

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __unicode__(self):
        return self.backend_name
        """
        output_array = [
            self.backend_name,
            ' (',
            self.user.id,
            ')'
        ]
        return ''.join([s for s in output_array])
        """

    objects = BusinessManager()

    def update(
        self,
        name=None,
        summary=None,
        description=None,
        address=None,
        phone=None,
        twitter_name=None,
        facebook_uri=None,
        yelp_id=None
    ):
        is_self_dirty = False

        if None != name:
            if name != self.business_name.value:
                backend_name = urlquote(name.strip().lower().replace(' ', '-'))
                self.backend_name = backend_name
                self.business_name = self.business_name.update(name)
                is_self_dirty = True

        if None != summary:
            current_summary = self.summary.value if self.summary else None
            if summary != current_summary:
                if self.summary:
                    self.summary = self.summary.update(summary)
                else:
                    self.summary = Content.objects.create(
                        content_type=ContentTypes.BUSINESS_SUMMARY,
                        user=self.user,
                        name=self.backend_name + '_summary',
                        parent=self.content_root,
                        value=summary
                    )
                is_self_dirty = True

        if None != description:
            current_description = self.description.value if self.description else None
            if description != current_description:
                if self.description:
                    self.description = self.description.update(description)
                else:
                    self.description = Content.objects.create(
                        content_type=ContentTypes.BUSINESS_DESCRIPTION,
                        user=self.user,
                        name=self.backend_name + '_description',
                        parent=self.content_root,
                        value=description
                    )
                is_self_dirty = True

        if None != address:
            current_address = self.address.value.value if self.address else None
            if address != current_address:
                if self.address:
                    self.address.update(address)
                else:
                    self.address = EndpointAddress.objects.create(
                        user=self.user,
                        value=address
                    )
                    is_self_dirty = True

        if None != phone:
            current_phone = self.phone.value.value if self.phone else None
            if phone != current_phone:
                if self.phone:
                    self.phone.update(phone)
                else:
                    self.phone = EndpointPhone.objects.create(
                        user=self.user,
                        value=phone
                    )
                    is_self_dirty = True

        if None != twitter_name:
            current_twitter = self.twitter_name.value.value if self.twitter_name else None
            if twitter_name != current_twitter:
                if self.twitter_name:
                    self.twitter_name.update(twitter_name)
                else:
                    self.twitter_name = EndpointTwitter.objects.create(
                        user=self.user,
                        value=twitter_name
                    )
                    is_self_dirty = True

        if None != facebook_uri:
            current_facebook = self.facebook_uri.value.value if self.facebook_uri else None
            if facebook_uri != current_facebook:
                if self.facebook_uri:
                    self.facebook_uri.update(facebook_uri)
                else:
                    self.facebook_uri = EndpointFacebook.objects.create(
                        user=self.user,
                        value=facebook_uri
                    )
                    is_self_dirty = True

        if None != yelp_id:
            current_yelp = self.yelp_id.value.value if self.yelp_id else None
            if yelp_id != current_yelp:
                if self.yelp_id:
                    self.yelp_id.update(yelp_id)
                else:
                    self.yelp_id = EndpointYelp.objects.create(
                        user=self.user,
                        value=yelp_id
                    )
                    is_self_dirty = True

        if is_self_dirty:
            self.save()


class BusinessLink(KnotisModel):
    business = ForeignKeyNonRel(Business)
    uri = URLField()
    title = CharField(max_length=64)


class BusinessSubscriptionManager(Manager):
    def get_users_subscribed_to_business(
        self,
        business,
        subscriptions=None
    ):
        if not subscriptions:
            try:
                subscriptions = BusinessSubscription.objects.filter(
                    business=business,
                    active=True
                )
            except:
                pass

        if not subscriptions:
            return None

        users = []
        for subscription in subscriptions:
            users.append(subscription.user)

        return users


class BusinessSubscription(KnotisModel):
    user = ForeignKeyNonRel(User)
    business = ForeignKeyNonRel(Business)
    active = NullBooleanField(default=True, blank=True, db_index=True)

    objects = BusinessSubscriptionManager()

    def get_user_avatar(self):
        return self.user.avatar

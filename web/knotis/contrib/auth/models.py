import hashlib

from django.utils import log
logger = log.getLogger(__name__)

from django.contrib.auth.models import (
    UserManager,
    User as DjangoUser
)
from django.db.models import (
    Model,
    Manager,
    CharField,
    IntegerField,
    DateTimeField
)
from django_extensions.db.fields import UUIDField

from knotis.contrib.core.models import KnotisModel
from knotis.contrib.denormalize.models import DenormalizedField
from knotis.contrib.facebook.views import get_facebook_avatar
from knotis.contrib.gravatar.views import avatar as get_gravatar_avatar
from knotis.contrib.cassandra.models import ForeignKey
from knotis.contrib.endpoint.models import Endpoint
from knotis.contrib.media.models import Image
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)


class AccountTypes:
    USER = 'user'
    BUSINESS_FREE = 'foreverfree'
    BUSINESS_MONTHLY = 'premium'

    CHOICES = (
        (USER, 'User'),
        (BUSINESS_FREE, 'Business - Free'),
        (BUSINESS_MONTHLY, 'Business - Monthly'),
    )


class AccountStatus:
    NEW = 0
    ACTIVE = 1
    DISABLED = 2
    BANNED = 3

    CHOICES = (
        (NEW, 'New'),
        (ACTIVE, 'Active'),
        (DISABLED, 'Disabled'),
        (BANNED, 'Banned')
    )


class KnotisUserManager(UserManager):
    def create_user(
        self,
        first_name,
        last_name,
        email,
        password
    ):
        if email:
            email = email.lower()

        new_user = super(KnotisUserManager, self).create_user(
            email,
            email,
            password
        )

        new_user.first_name = first_name
        new_user.last_name = last_name

        new_user.save()

        identity = Identity.objects.create(
            owner=new_user,
            name=' '.join([
                first_name,
                last_name
            ]),
            identity_type=IdentityTypes.INDIVIDUAL
        )

        UserInformation.objects.create(
            new_user,
            identity
        )

        return new_user, identity


class KnotisUser(DjangoUser):
    class Meta:
        proxy = True

    objects = KnotisUserManager()

    def check_password(
        self,
        raw_password
    ):
        if super(KnotisUser, self).check_password(raw_password):
            return True

        algorithm, salt, digest = self.password.split('$')

        if 'sha1' != algorithm.lower():
            return False

        reverse_sha = hashlib.sha1()
        reverse_sha.update(raw_password)
        reverse_sha.update(salt)

        return digest == unicode(reverse_sha.hexdigest())

    def username_12(self):
        return ''.join([
            self.username[:9],
            '...'
        ])

    def avatar(
        self,
        facebook_id=None
    ):
        if facebook_id:
            return get_facebook_avatar(facebook_id)
        else:
            return get_gravatar_avatar(
                self.username,
                32,
                'mm',
                'g',
                False,
                {}
            )


class UserInformationManager(Manager):
    def create(
        self,
        user,
        default_identity
    ):
        user_information = UserInformation()
        user_information.id = user.id
        user_information.username = user
        user_information.default_identity = default_identity
        user_information.default_identity_type = default_identity
        user_information.default_identity_name = default_identity
        if default_identity.primary_image:
            user_information.default_identity_image = (
                default_identity.primary_image
            )
        user_information.save()
        return user_information


class UserInformation(KnotisModel):
    id = UUIDField(primary_key=True)
    username = DenormalizedField(KnotisUser)
    default_identity = ForeignKey(Identity)
    default_identity_type = DenormalizedField(Identity, 'identity_type')
    default_identity_name = DenormalizedField(Identity, 'name')
    default_identity_image = DenormalizedField(Image, 'image')

    objects = UserInformationManager()


class CredentialsTypes:
    FACEBOOK = 0

    CHOICES = (
        (FACEBOOK, 'Facebook'),
    )


class Credentials(Model):
    user = ForeignKey(KnotisUser)
    credentials_type = IntegerField(
        choices=CredentialsTypes.CHOICES,
        null=True,
        blank=True,
        default=CredentialsTypes.FACEBOOK
    )
    user_identifier = CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None
    )
    value = CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None
    )


class PasswordReset(KnotisModel):
    endpoint = ForeignKey(Endpoint)
    password_reset_key = CharField(
        max_length=36,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    expires = DateTimeField()

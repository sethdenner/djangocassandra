import hashlib

from django.utils import log
logger = log.getLogger(__name__)

from django.contrib.auth.models import (
    UserManager,
    User as DjangoUser
)
from django.db.models import (
    Manager,
    Model,
    CharField,
    IntegerField,
)

from knotis.contrib.core.models import KnotisModel
from knotis.contrib.facebook.views import get_facebook_avatar
from knotis.contrib.gravatar.views import avatar as get_gravatar_avatar
from knotis.contrib.cassandra.models import ForeignKey
from knotis.contrib.endpoint.models import Endpoint
from knotis.contrib.identity.models import (
    Identity,
    IdentityIndividual,
    IdentityTypes
)
from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
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
        password,
        account_type=AccountTypes.USER
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
            name=' '.join([first_name, last_name]),
            identity_type=IdentityTypes.INDIVIDUAL
        )

        Relation.objects.create(
            owner=new_user,
            subject=identity,
            relation_type=RelationTypes.OWNER
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

    def update(
        self,
        username=None,
        first_name=None,
        last_name=None,
    ):
        is_self_dirty = False

        if username:
            if username != self.username:
                self.username = username
                is_self_dirty = True

        if first_name:
            if first_name != self.first_name:
                self.first_name = first_name
                is_self_dirty = True

        if last_name:
            if last_name != self.last_name:
                self.last_name = last_name
                is_self_dirty = True

        if is_self_dirty:
            self.save()


class UserProfileManager(Manager):
    def create_profile(
        self,
        user,
        account_type=AccountTypes.USER
    ):
        user_profile = UserProfile(
            user=user,
            account_type=account_type
        )
        user_profile.save()

        return user_profile

    def activate_profile(
        self,
        user
    ):
        user_profile = self.get(pk=user)
        user_profile.activate()


class UserProfile(IdentityIndividual):
    objects = UserProfileManager()

    def __unicode__(self):
        return self.user.username

    def is_business_owner(self):
        return self.identity_type == IdentityTypes.BUSINESS


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

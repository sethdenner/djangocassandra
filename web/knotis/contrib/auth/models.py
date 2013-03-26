import hashlib

from django.utils import log
logger = log.getLogger(__name__)

from django.contrib.auth.models import (
    UserManager,
    User as DjangoUser
)
from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickDateTimeField,
    QuickForeignKey
)
from knotis.contrib.denormalize.models import DenormalizedField
from knotis.contrib.facebook.views import get_facebook_avatar
from knotis.contrib.gravatar.views import avatar as get_gravatar_avatar
from knotis.contrib.endpoint.models import Endpoint
from knotis.contrib.media.models import Image
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
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


class UserInformationManager(QuickManager):
    pass


class UserInformation(QuickModel):
    username = DenormalizedField(
        KnotisUser,
        'username'
    )
    default_identity = QuickForeignKey(Identity)

    objects = UserInformationManager()


class PasswordReset(QuickModel):
    endpoint = QuickForeignKey(Endpoint)
    password_reset_key = QuickCharField(
        max_length=36,
        db_index=True
    )
    expires = QuickDateTimeField()

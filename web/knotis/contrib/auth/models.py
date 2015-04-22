import hashlib

''' Needs to be replaced with django 1.7 compatable alternative.
from doac.models import Client as DoacClient
'''
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
    QuickBooleanField,
    QuickDateTimeField,
    QuickForeignKey
)
from knotis.contrib.denormalize.models import DenormalizedField
from knotis.contrib.identity.models import Identity
from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)


class KnotisUserManager(UserManager):
    def create_user(
        self,
        email,
        password,
        is_superuser=False
    ):
        if email:
            email = email.lower()

        new_user = super(KnotisUserManager, self).create_user(
            email,
            email,
            password
        )

        if is_superuser:
            new_user.is_superuser = is_superuser
            new_user.save()

        user_info = UserInformation()
        user_info.user = new_user
        user_info.username = new_user
        user_info.save()

        return new_user, user_info

    def get_identity_user(
        self,
        identity,
    ):
        relations = Relation.objects.filter(
            relation_type=RelationTypes.INDIVIDUAL,
            related_object_id=identity.pk
        )

        return relations[0].subject


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

    def full_name(self):
        return ' '.join([
            self.first_name,
            self.last_name
        ]).strip()

    def username_12(self):
        return ''.join([
            self.username[:9],
            '...'
        ])


class UserInformationManager(QuickManager):
    pass


class UserInformation(QuickModel):
    user = QuickForeignKey(DjangoUser)
    username = DenormalizedField(
        DjangoUser,
        'username'
    )
    default_identity = QuickForeignKey(Identity)
    mobile_app_installed = QuickBooleanField(default=False)

    objects = UserInformationManager()


class PasswordReset(QuickModel):
    user = QuickForeignKey(DjangoUser)
    password_reset_key = QuickCharField(
        max_length=36,
        db_index=True
    )
    expires = QuickDateTimeField()


class UserXapiClientMap(QuickModel):
    user = QuickForeignKey(DjangoUser)
    client = QuickCharField(max_length=64)

import hashlib

from django.contrib.auth import models
from django.db.models import Model, CharField, OneToOneField, \
    FloatField, IntegerField, NullBooleanField, Manager

from gravatar.views import avatar as gravatar_avatar
from facebook.views import get_facebook_avatar

from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.fields.math import MatrixField


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
    DISABLED = 0
    ACTIVE = 1

    CHOICES = (
        (DISABLED, 'Disabled'),
        (ACTIVE, 'Active')
    )


class UserManager(models.UserManager):
    def create_user(
        self,
        first_name,
        last_name,
        email,
        password,
        account_type=AccountTypes.USER,
        business=False
    ):
        if email:
            email = email.lower()
            
        new_user = super(UserManager, self).create_user(
            email,
            email,
            password
        )

        new_user.first_name = first_name
        new_user.last_name = last_name

        new_user.save()

        account_type = account_type if business else AccountTypes.USER

        user_profile = UserProfile.objects.create_profile(
            new_user,
            account_type
        )

        return new_user, user_profile


class User(models.User):
    class Meta:
        proxy = True

    objects = UserManager()

    def check_pasword(
        self,
        raw_password
    ):
        if super(User, self).check_password(raw_password):
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
            return gravatar_avatar(
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
        user_profile.account_status = AccountStatus.ACTIVE
        user_profile.save()


class UserProfile(Model):
    user = OneToOneField(User, primary_key=True)

    account_type = CharField(
        max_length=32,
        null=True,
        choices=AccountTypes.CHOICES,
        default=AccountTypes.USER
    )
    account_status = IntegerField(
        null=True,
        choices=AccountStatus.CHOICES,
        default=AccountStatus.DISABLED
    )

    notify_announcements = NullBooleanField(blank=True, default=False)
    notify_offers = NullBooleanField(blank=True, default=False)
    notify_events = NullBooleanField(blank=True, default=False)

    password_reset_key = CharField(
        max_length=36,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )

    reputation_mu = FloatField(null=True, default=1.)
    reputation_sigma = FloatField(null=True, default=0.)
    reputation_total = FloatField(null=True, default=0.)
    reputation_matrix = MatrixField(null=True, blank=True, max_length=200)

    objects = UserProfileManager()

    def __unicode__(self):
        return self.user.username

    def is_business_owner(self):
        return self.account_type != AccountTypes.USER

    def update(
        self,
        account_type=None,
        account_status=None,
        notify_announcements=None,
        notify_offers=None,
        notify_events=None,
        reputation_mu=None,
        reputation_sigma=None,
        reputation_total=None,
        reputation_matrix=None
    ):
        is_self_dirty = False

        if None != account_type:
            if account_type != self.account_type:
                self.account_type = account_type
                is_self_dirty = True

        if None != account_status:
            if account_status != self.account_status:
                self.account_status = account_status
                is_self_dirty = True

        if None != notify_announcements:
            if notify_announcements != self.notify_announcements:
                self.notify_announcements = notify_announcements
                is_self_dirty = True

        if None != notify_offers:
            if notify_offers != self.notify_offers:
                self.notify_offers = notify_offers
                is_self_dirty = True

        if None != notify_events:
            if notify_events != self.notify_events:
                self.notify_events = notify_events
                is_self_dirty = True

        if None != reputation_mu:
            if reputation_mu != self.reputation_mu:
                self.reputation_mu = reputation_mu
                is_self_dirty = True

        if None != reputation_sigma:
            if reputation_sigma != self.reputation_sigma:
                self.reputation_sigma = reputation_sigma
                is_self_dirty = True

        if None != reputation_total:
            if reputation_total != self.reputation_total:
                self.reputation_total = reputation_total
                is_self_dirty = True

        if None != reputation_matrix:
            if reputation_matrix != self.reputation_matrix:
                self.reputation_matrix = reputation_matrix
                is_self_dirty = True

        if is_self_dirty:
            self.save()


class CredentialsTypes:
    FACEBOOK = 0

    CHOICES = (
        (FACEBOOK, 'Facebook'),
    )


class Credentials(Model):
    user = ForeignKeyNonRel(User)
    credentials_type = IntegerField(choices=CredentialsTypes.CHOICES, null=True, blank=True, default=CredentialsTypes.FACEBOOK)
    user_identifier = CharField(max_length=256, null=True, blank=True, default=None)
    value = CharField(max_length=256, null=True, blank=True, default=None)

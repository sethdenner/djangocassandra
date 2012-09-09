from django.db.models import OneToOneField, FloatField, IntegerField, \
    NullBooleanField, Manager
from django.contrib.auth.models import User

from app.models.knotis import KnotisModel
from app.models.fields.math import MatrixField


class AccountTypes:
    USER = 0
    BUSINESS_FREE = 1
    BUSINESS_MONTHLY = 2

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


class UserProfile(KnotisModel):
    user = OneToOneField(User, primary_key=True)

    account_type = IntegerField(null=True, choices=AccountTypes.CHOICES, default=AccountTypes.USER)
    account_status = IntegerField(null=True, choices=AccountStatus.CHOICES, default=AccountStatus.DISABLED)

    notify_announcements = NullBooleanField(blank=True, default=False)
    notify_offers = NullBooleanField(blank=True, default=False)
    notify_events = NullBooleanField(blank=True, default=False)

    reputation_mu = FloatField(null=True, default=1.)
    reputation_sigma = FloatField(null=True, default=0.)
    reputation_total = FloatField(null=True, default=0.)
    reputation_matrix = MatrixField(null=True, blank=True, max_length=200)

    objects = UserProfileManager()

    def is_business_owner(self):
        return True if self.account_type != 0 else False

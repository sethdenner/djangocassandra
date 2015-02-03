import random
from knotis.contrib.identity.api import (
    IdentityApi
)
from knotis.contrib.auth.tests.utils import UserCreationTestUtils
from knotis.contrib.media.tests.utils import MediaTestUtils


class IdentityModelTestUtils(object):
    @staticmethod
    def create_test_business(
        manager=None,
        **kwargs
    ):
        unique = str(random.randint(0, 100000))
        if manager is None:
            _, manager = UserCreationTestUtils.create_test_user()

        if not kwargs.get('name'):
            kwargs['name'] = 'Test Business' + unique

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Business description.' + unique

        business, establishment = IdentityApi.create_business(
            individual_id=manager.id,
            **kwargs
        )
        if not kwargs.get('no_profile_badge'):
            MediaTestUtils.create_test_image(
                owner=business,
                context='profile_badge'
            )

        if not kwargs.get('no_profile_banner'):
            MediaTestUtils.create_test_image(
                owner=business,
                context='profile_banner'
            )

        return business, establishment

    @staticmethod
    def create_test_establishment(
        business=None,
        **kwargs
    ):
        unique = str(random.randint(0, 100000))

        if not kwargs.get('name'):
            kwargs['name'] = 'Test Establishment' + unique

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Establishment description.' + unique

        if business is None:
            business, establishment = \
                IdentityModelTestUtils.create_test_business(**kwargs)
        else:
            establishment = IdentityApi.create_establishment(
                business_id=business.id,
                **kwargs
            )

        if not kwargs.get('no_profile_badge'):
            MediaTestUtils.create_test_image(
                owner=establishment,
                context='profile_badge'
            )

        if not kwargs.get('no_profile_banner'):
            MediaTestUtils.create_test_image(
                owner=establishment,
                context='profile_banner'
            )

        return establishment

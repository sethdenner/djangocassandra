from knotis.contrib.identity.models import (
    IdentityBusiness,
    IdentityEstablishment
)
from knotis.contrib.auth.tests.utils import UserCreationTestUtils


class IdentityModelTestUtils(object):
    @staticmethod
    def create_test_business(
        manager=None,
        **kwargs
    ):
        if manager is None:
            _, manager = UserCreationTestUtils.create_test_user()

        if not kwargs.get('name'):
            kwargs['name'] = 'Test Business'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Business description.'

        return IdentityBusiness.objects.create(
            manager,
            **kwargs
        )

    @staticmethod
    def create_test_establishment(
        business=None,
        **kwargs
    ):
        if business is None:
            business = IdentityModelTestUtils.create_test_business()

        if not kwargs.get('name'):
            kwargs['name'] = 'Test Establishment'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Establishment description.'

        return IdentityEstablishment.objects.create(
            business,
            **kwargs
        )

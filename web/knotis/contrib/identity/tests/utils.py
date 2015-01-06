from knotis.contrib.identity.models import (
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)


class IdentityModelTestUtils(object):
    @staticmethod
    def create_test_individual(**kwargs):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Individual'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Individual description.'

        return IdentityIndividual.objects.create(**kwargs)

    @staticmethod
    def create_test_business(
        manager,
        **kwargs
    ):
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
        business,
        **kwargs
    ):
        if not kwargs.get('name'):
            kwargs['name'] = 'Test Establishment'

        if not kwargs.get('description'):
            kwargs['description'] = 'Test Establishment description.'

        return IdentityEstablishment.objects.create(
            business,
            **kwargs
        )

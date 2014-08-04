from django.core.management.base import BaseCommand

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import IdentityIndividual
from knotis.contrib.endpoint.models import Endpoint, EndpointTypes
import settings

class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        user_name = args[0]
        knotis_user = KnotisUser.objects.get(username=user_name)
        identity = IdentityIndividual.objects.get_individual(knotis_user)
        endpoint = Endpoint.objects.get(
            identity=identity,
            endpoint_type=EndpointTypes.EMAIL,
            primary=True,
        )

        activation_link = '/'.join([
            settings.BASE_URL,
            'auth/validate',
            knotis_user.id,
            endpoint.validation_key,
            ''
        ])
        print activation_link

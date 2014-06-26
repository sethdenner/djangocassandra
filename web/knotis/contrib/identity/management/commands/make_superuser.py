from django.core.management.base import BaseCommand

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import IdentitySuperUser

class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        user_name = args[0]
        knotis_user = KnotisUser.objects.get(username=user_name)
        IdentitySuperUser.objects.create(knotis_user)

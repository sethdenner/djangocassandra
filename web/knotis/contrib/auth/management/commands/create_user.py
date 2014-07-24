from django.core.management.base import BaseCommand
from optparse import make_option

from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.auth.forms import CreateUserForm
from knotis.contrib.auth.api import AuthenticationApi

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--name',
            dest='name',
            default=None,
            help='Name for the new user.'),
        make_option('--is_superuser',
            dest='is_superuser',
            action="store_true",
            default=False,
            help='If the offer is for a physical item'),
    )
    def handle(
        self,
        *args,
        **options
    ):
        if len(args) > 2:
            raise Exception("Not enough arguements")
        email = args[0]

        password = args[1]

        #data = {'email':email, 'password':password}
        #form = CreateUserForm(
        #    True,
        #    data
        #)
        #user, identity = form.save(is_superuser=options.get('is_superuser'))
        user, identity, errors = AuthenticationApi.create_user(
            send_validation=False,
            email=email,
            password=password,
        )


        name = options.get('name', None)
        if name:
            identity.name = name
            identity.save()

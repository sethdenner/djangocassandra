import json

from django.utils import log
logger = log.getLogger(__name__)

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.apps.auth.models import KnotisUser
from knotis.apps.business.models import Business

class Command(BaseCommand):
    args = '<json_file>'
    help = (
        'Zips up businesses and users in specified json file with format:\n'
        '    {\n'
        '        "<business.backend_name>": "<user.username>", ...\n'
        '    }'
    )

    def handle(
        self,
        *args,
        **options
    ):
        if not args:
            raise CommandError('No file specified')
        
        try:
            data = json.loads(open(args[0]).read())
            
        except:
            msg = 'failed to load input data'
            logger.exception(msg)
            raise CommandError(msg)
        
        for backend_name, username in data.items():
            try:
                business = Business.objects.get(backend_name=backend_name)
                
            except:
                logger.exception('could not get business %s' % (backend_name, ))
                continue
            
            if business.user:
                logger.error(
                    'business "%s" is already owned by user "%s" (skipping)' % (
                        business.business_name.value, 
                        business.user.username
                    )
                )
                continue

            try:
                user = KnotisUser.objects.get(username=username)
                
            except:
                logger.exception('could not get user %s' % (username, ))
                continue
            
            logger.info(
                'assigning user "%s" to business "%s' % (
                    user.username, 
                    business.business_name.value
                )
            )
            
            business.user = user
            try:
                business.save()
                
            except:
                logger.exception('failed to save business')
        
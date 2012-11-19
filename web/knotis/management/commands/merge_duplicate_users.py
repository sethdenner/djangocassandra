from django.utils import log
logger = log.getLogger(__name__)

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.apps.auth.models import (
    KnotisUser,
    UserProfile
)
from knotis.apps.business.models import (
    Business,
    BusinessSubscription
)
from knotis.apps.content.models import Content
from knotis.apps.endpoint.models import Endpoint 
from knotis.apps.transaction.models import Transaction
from knotis.apps.legacy.models import UserIdMap
from knotis.apps.media.models import Image

class Command(BaseCommand):
    args = ''
    help = (
        'This commands finds duplicate users in the database and merges them'
    )
    
    def handle(
        self,
        *args,
        **options
    ):
        try:
            users = KnotisUser.objects.all()
            
        except:
            msg = 'failed to get users'
            logger.exception(msg)
            raise CommandError(msg)
        
        sorted_users = sorted(list(users), key=lambda user: user.username)
        duplicate_users = []
        i = 0
        while i < len(sorted_users) - 1:
            if sorted_users[i].username == sorted_users[i+1].username:
                duplicate_users.append((sorted_users[i], sorted_users[i+1]))
                i += 2
                
            else:
                i += 1
                
        if not duplicate_users:
            logger.info('no duplicate users (exiting)')
            return                
                
        for user0, user1 in duplicate_users:
            logger.info(
                'merging users "%s" and "%s"' % (
                    user0.id, 
                    user1.id
                )
            )
            clean_merge = True
            
            logger.info('merging businesses')
            try:
                business0 = Business.objects.get(user=user0)
            
            except:
                business0 = None
                
            try:
                business1 = Business.objects.get(user=user1)
                
            except:
                business1 = None
                
            if business1:
                if not business0:
                    business1.user = user0
                    try:
                        business1.save()
                
                    except:
                        logger.exception('failed to merge businesses')
                        clean_merge = False
                
            try:
                logger.info('merging subscriptions')
                subscriptions1 = BusinessSubscription.objects.filter(user=user1)
                if subscriptions1:
                    for subscription in subscriptions1:
                        subscription.user = user0
                        subscription.save()
                
            except:
                logger.exception('failed to merge subscriptions')
                clean_merge = False
                
            try:
                logger.info('merging content')
                content1 = Content.objects.filter(user=user1)
                if content1:
                    for content in content1:
                        content.user = user0
                        content.save()
                    
            except:
                logger.exception('failed to merge content')
                clean_merge = False
                
            try:
                logger.info('merging endpoints')
                endpoints1 = Endpoint.objects.filter(user=user1)
                if endpoints1:
                    for endpoint in endpoints1:
                        endpoint.user = user0
                        endpoint.save()
                        
            except:
                logger.exception('failed to merge endpoints')
                clean_merge = False

            try:
                logger.info('merging transactions')
                transactions1 = Transaction.objects.filter(user=user1)
                if transactions1:
                    for transaction in transactions1:
                        transaction.user = user0
                        transaction.save()
                        
            except:
                logger.exception('failed to merge businesses')
                clean_merge = False

            try:
                logger.info('merging images')
                images1 = Image.objects.filter(user=user1)
                if images1:
                    for image in images1:
                        image.user = user0
                        image.save()
                        
            except:
                logger.exception('failed to merge images')
                clean_merge = False
                
            if not clean_merge:
                logger.info(
                    'merge was not clean fix data issues and run again to '
                    'delete duplicate user'
                )
                
            else:
                logger.info('merge clean, deleting user %s' % (user1.id, ))
                try:
                    user1.delete()
                    
                    try:
                        user1_id_map = UserIdMap.objects.get(new_user=user1)

                    except:
                        user1_id_map = None
                    
                    if user1_id_map:
                        user1.id_map.delete()
                        
                    try:
                        user1_profile = UserProfile.objects.get(user=user1)
                        
                    except:
                        user1_profile = None
                        
                    if user1_profile:
                        user1_profile.delete()
                    
                    
                except:
                    logger.exception('failed to delete duplicate user')

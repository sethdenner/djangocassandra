from django.utils import log
logger = log.getLogger(__name__)

from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError
)

from knotis.apps.business.models import Business
from knotis.apps.qrcode.models import (
    Qrcode,
    QrcodeTypes
)

class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        try:
            businesses = Business.objects.all()
            
        except:
            msg = 'failed to get businesses'
            logger.exception(msg)
            raise CommandError(msg)
        
        sorted_businesses = sorted(list(businesses), key=lambda b: b.backend_name)
        duplicates = []
        i = 0
        while i < len(sorted_businesses) - 1:
            if sorted_businesses[i].backend_name == sorted_businesses[i + 1].backend_name:
                duplicates.append((sorted_businesses[i], sorted_businesses[i + 1]))
                i += 2
                
            else:
                i += 1
                
        if not duplicates:
            logger.info('no duplicates (exiting)')
            return
                
        for b1, b2 in duplicates:
            try:
                logger.info(
                    'changing "%s" to "%s-2"' % (
                        b1.backend_name, 
                        b2.backend_name
                    )
                )
                b2.backend_name += '-2'
                b2.save()
                
                try:
                    qrcode = Qrcode.objects.get(business=b2)

                except:
                    qrcode = None
                    
                if qrcode:
                    if QrcodeTypes.PROFILE == qrcode.qrcode_type:
                        qrcode.uri = '/'.join([
                            settings.BASE_URL,
                            b2.backend_name,
                            ''
                        ])
                        qrcode.save()
            
            except:
                logger.exception(
                    'failed to save business %s' % (b2.business_name.value, )
                )

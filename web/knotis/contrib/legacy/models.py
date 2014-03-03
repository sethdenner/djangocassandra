import json

from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.db.models import (
    IntegerField,
    ForeignKey,
    Model,
    Manager
)

from knotis.contrib.qrcode.models import Qrcode

from knotis.contrib.identity.models import (
    IdentityBusiness,
    IdentityEstablishment
)


class QrcodeIdMapManager(Manager):
    def create_from_business(
        self,
        business,
        old_id
    ):
        qrcode = Qrcode.objects.filter(owner=business)[0]
        existing = QrcodeIdMap.objects.filter(old_id=old_id)
        if len(existing):
            qrcode_map = existing[0]
            qrcode_map.new_qrcode = qrcode
            qrcode_map.save()
            return qrcode_map

        else:
            return self.create(
                old_id=old_id,
                new_qrcode=qrcode
            )


class QrcodeIdMap(Model):
    old_id = IntegerField(
        db_index=True,
        null=False,
        blank=False
    )
    new_qrcode = ForeignKey(Qrcode)

    objects = QrcodeIdMapManager()


def legacy_id_import(filename):
    '''
    This method expects a filename that points to a json file
    that consists of an array of objects with two members:

        legacy_business_id and establishment_id (in that order)
    '''
    raw = open(filename).read()
    data = json.loads(raw)

    for r in data:
        try:
            establishment = IdentityEstablishment.objects.get(
                pk=r['establishment_id']
            )

        except:
            logger.exception(
                'Failed to get establishment with id %s' % (
                    r['establishment_id']
                )
            )
            continue

        try:
            business = IdentityBusiness.objects.get_establishment_parent(
                establishment
            )

        except:
            logger.exception(
                'Failed to get business for establishment %s' % (
                    establishment.name
                )
            )
            continue

        try:
            QrcodeIdMap.objects.create_from_business(
                business,
                r['legacy_business_id']
            )
            logger.info('Created QrcodeIdMap object for: %s (%s)' % (
                business.name,
                r['legacy_business_id']
            ))

        except:
            logger.exception(
                'Failed to create QrcodeIdMap for business %s' % (
                    business.name
                )
            )
            continue

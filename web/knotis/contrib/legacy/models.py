from django.db.models import (
    IntegerField,
    ForeignKey,
    Model,
    Manager
)

from knotis.contrib.qrcode.models import Qrcode


class QrcodeIdMapManager(Manager):
    def create_from_business(
        self,
        business,
        old_id
    ):
        qrcode = Qrcode.objects.filter(owner=business)[0]
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

from django.db.models import URLField, IntegerField, CharField, DateTimeField
from django.shortcuts import redirect

from app.models.knotis import KnotisModel
from app.models.businesses import Business

from foreignkeynonrel.models import ForeignKeyNonRel


class QrcodeTypes:
    PROFILE = 'profile'
    LINK = 'link'
    VIDEO = 'video'
    OFFER = 'offer'

    CHOICES = (
        (PROFILE, 'Business Profile'),
        (LINK, 'External Link'),
        (VIDEO, 'Video'),
        (OFFER, 'Offer')
    )


class Qrcode(KnotisModel):
    business = ForeignKeyNonRel(Business)
    uri = URLField(blank=True, null=True)
    qrcode_type = CharField(
        max_length=16,
        choices=QrcodeTypes.CHOICES,
        null=True,
        default=QrcodeTypes.PROFILE,
        db_index=True
    )
    hits = IntegerField(blank=True, null=True, default=0)
    last_hit = DateTimeField(auto_now=True, blank=True, null=True)
    pub_date = DateTimeField(auto_now_add=True, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Qrcode, self).__init__(*args, **kwargs)

    def scan(self):
        try:
            Scan.objects.create(
                qrcode=self,
                uri=self.uri
            )

            self.hits = self.hits + 1
            self.save()
        except:
            pass

        return redirect(self.uri)


class Scan(KnotisModel):
    qrcode = ForeignKeyNonRel(Qrcode)
    uri = URLField(blank=True, null=True, db_index=True)
    pub_date = DateTimeField(auto_now_add=True)

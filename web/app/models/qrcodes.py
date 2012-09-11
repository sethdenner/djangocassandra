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
    qrcode_type = CharField(max_length=16, choices=QrcodeTypes.CHOICES, null=True, default=QrcodeTypes.PROFILE, db_index=True)
    hits = IntegerField(blank=True, null=True, default=0)

    def __init__(self, *args, **kwargs):

        super(Qrcode, self).__init__(*args, **kwargs)

    def scan(self):
        self.hits = self.hits + 1
        self.save()

        scan = None
        try:
            scan = Scan.objects.filter(qrcode=self, uri=self.uri)[0]
        except:
            pass

        if scan:
            scan.hits = scan.hits + 1
            scan.save()
        else:
            Scan.objects.create(
                qrcode=self,
                uri=self.uri,
                hits=1
            )

        return redirect(self.uri)


class Scan(KnotisModel):
    qrcode = ForeignKeyNonRel(Qrcode)
    uri = URLField(blank=True, null=True, db_index=True)
    hits = IntegerField(default=0, blank=True, null=True)
    last_hit = DateTimeField(auto_now=True)
    pub_date = DateTimeField(auto_now_add=True)

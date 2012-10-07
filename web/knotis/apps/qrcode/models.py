import datetime
import itertools

from django.db.models import URLField, IntegerField, CharField, DateTimeField, \
    Manager
from django.shortcuts import redirect

from knotis.models.abstract import KnotisModel
from knotis.models.business import Business
from knotis.models import ForeignKey


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
    business = ForeignKey(Business)
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
                business=self.business,
                uri=self.uri
            )

            self.hits = self.hits + 1
            self.save()
        except:
            pass

        return redirect(self.uri)


class ScanManager(Manager):
    def get_daily_scans(
        self,
        business
    ):
        scans = self.filter(business=business)

        daily_scans = []
        day = 0
        while day < 7:
            daily_scans.append(0)
            day = day + 1

        for scan in scans:
            scan_date = scan.pub_date
            now = datetime.datetime.utcnow()
            if scan_date < now - datetime.timedelta(weeks=1):
                continue

            day_index = scan_date.weekday() + (6 - now.weekday())
            if day_index > 6:
                day_index = day_index - 6

            daily_scans[day_index] = \
                daily_scans[day_index] + 1

        return daily_scans

    def get_weekly_scans(
        self,
        business
    ):
        scans = self.filter(business=business)

        now = datetime.datetime.utcnow()
        now_week = now.isocalendar()[1]
        start_week = now_week - 7

        def week(date):
            week = date.isocalendar()[1] - start_week
            return week

        scan_values = [(scan.pub_date, scan.id) for scan in scans]
        scan_values.sort(key=lambda (date, value):date)

        weekly_scans = []
        week_count = 0
        while week_count < 7:
            weekly_scans.append(0.)
            week_count = week_count + 1

        for key, group in itertools.groupby(
            scan_values,
            key=lambda (date, value): week(date)
        ):
            if key < 0:
                continue

            index = key - 1
            for item in group:
                weekly_scans[index] = weekly_scans[index] + 1

        return weekly_scans

    def get_monthly_scans(
        self,
        business
    ):
        scans = self.filter(business=business)

        monthly_scans = []
        month = 0
        while month < 12:
            monthly_scans.append(0.)
            month = month + 1

        for scan in scans:
            month = scan.pub_date.month
            if month < 1 or month > 12:
                continue

            now = datetime.datetime.utcnow()
            month_index = month + (12 - now.month)
            if month_index > 12:
                month_index = month_index - 12

            month_index = month_index - 1

            monthly_scans[month_index] = \
                monthly_scans[month_index] + 1

        return monthly_scans


class Scan(KnotisModel):
    qrcode = ForeignKey(Qrcode)
    business = ForeignKey(Business)
    uri = URLField(blank=True, null=True, db_index=True)
    pub_date = DateTimeField(auto_now_add=True)

    objects = ScanManager()

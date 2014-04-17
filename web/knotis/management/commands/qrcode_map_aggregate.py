from django.core.management.base import (
    BaseCommand,
    CommandError
)
from optparse import make_option
from datetime import datetime

from haystack.query import SearchQuerySet
from haystack.utils.geo import Point

from knotis.contrib.qrcode.models import Qrcode, Scan
from knotis.contrib.identity.models import IdentityBusiness
from knotis.contrib.location.models import LocationItem
import csv


def aggregate_qrcodes(
    lat_top, lon_left,
    lat_bot, lon_right,
    start_time, end_time,
    filename
):

    downtown_bottom_left = Point(lon_left, lat_bot)
    downtown_top_right = Point(lon_right, lat_top)

    # Do the bounding box query.
    sqs = SearchQuerySet().within(
        'location',
        downtown_bottom_left,
        downtown_top_right
    )

    with open(filename, 'w') as csv_file:
        csv_file.write((
            'QRCode_id, Establishment_id, Establishment_name, '
            'establishment_address, total, last\n'
        ))
        csv_writer = csv.writer(csv_file)

        for identity in sqs:
            business = IdentityBusiness.objects.get_establishment_parent(
                identity.object
            )

            qrcodes = Qrcode.objects.filter(owner=business)
            for q in qrcodes:
                scans = Scan.objects.filter(
                    qrcode=q,
                    pub_date__gt=start_time,
                    pub_date__lt=end_time
                )

                location_item = LocationItem.objects.get(
                    related_object_id=identity.pk)

                row = [
                    q.pk,
                    identity.pk,
                    identity.object.name,
                    location_item.location.address,
                    len(scans),
                    q.last_hit
                ]
                csv_writer.writerow(row)


class Command(BaseCommand):
    args = (
        '<lat top> <lon left> '
        '<lat bot> <lon right> '
        '<time start> <time end> '
        '<output csv>'
    )
    help = 'QRCode Aggregates within a rectangle'
    option_list = BaseCommand.option_list + (
        make_option(
            '--area',
            dest='area',
            default='90,-180,0,0',
            help=(
                'The comma separated lat/long box specified by upper '
                'left and lower right')),
        make_option(
            '--neighborhood',
            dest='neighborhood',
            help=(
                'The option for specifying the neighborhood. Includes: '
                'Capitol Hill, Ballard, Queen Ann, Green Lake, Lake Union')),
        make_option(
            '--output_file',
            dest='output_file',
            default='output.csv',
            help='Filename for output csv'),
        make_option(
            '--start_time',
            dest='start_time',
            default=0,
            help='Start time for the scan publish date'),
        make_option(
            '--end_time',
            dest='end_time',
            default=10000000000,
            help='End time for the scan publish date'),
    )

    neighborhood_map = {'test': [90, -180, 0, 0]}

    def handle(self, *args, **options):

        if options['neighborhood']:
            area = self.neighborhood_map[options['neighborhood']]
        else:
            area = [float(x) for x in options['area'].split(',')]

        lat_top, lon_left = area[0:2]
        lat_bot, lon_right = area[2:4]

        start_time, end_time = [
            datetime.fromtimestamp(int(x)) for x in
            options['start_time'], options['end_time']
        ]

        filename = options['output_file']
        aggregate_qrcodes(
            lat_top, lon_left,
            lat_bot, lon_right,
            start_time, end_time,
            filename
        )

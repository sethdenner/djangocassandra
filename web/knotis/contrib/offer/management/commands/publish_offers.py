from django.core.management.base import BaseCommand
from knotis.contrib.offer.models import OfferPublish


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **kwargs
    ):
        self.stdout.write('\nPublishing offers.\n')
        unpublished = OfferPublish.objects.filter(completed=False)

        self.stdout.write(''.join([
            'Query returned ',
            str(unpublished.count()),
            ' endpoints.\n'
        ]))

        publish_count = 0
        offer_count = 0
        offer_ids = []

        for u in unpublished:
            offer = u.subject
            self.stdout.write(''.join([
                'Publishing offer <',
                offer.id,
                '> ',
                offer.title,
                ' from: ',
                offer.owner.name,
                ' to: ',
                u.endpoint.value,
                '.\n'
            ]))

            try:
                u.publish()
                publish_count += 1

                if not offer.id in offer_ids:
                    offer_ids.append(offer.id)
                    offer_count += 1

            except Exception, e:
                self.stderr.write(''.join([
                    'Failed to publish offer <',
                    u.id,
                    '> exception was: "',
                    e.message,
                    '".\n"'
                ]))

        self.stdout.write(''.join([
            'Published ',
            str(offer_count),
            ' offers to ',
            str(publish_count),
            ' endpoints.\n'
        ]))

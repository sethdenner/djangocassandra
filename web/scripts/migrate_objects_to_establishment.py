from django.utils.log import logging
logger = logging.getLogger(__name__)


def move_offers_to_establishment():
    from knotis.contrib.offer.models import Offer
    from knotis.contrib.identity.models import (
        IdentityEstablishment,
        IdentityTypes
    )
    from knotis.contrib.transaction.models import Transaction

    offers_migrated_total = 0
    transactions_migrated_total = 0
    failed_offer_migrations = []
    failed_transction_migrations = []
    all_offers = Offer.objects.all()
    x = 0
    chunk_size = 20
    offer_chunk = all_offers[x:x + chunk_size]
    while len(offer_chunk):
        for o in offer_chunk:
            if IdentityTypes.BUSINESS != o.owner.identity_type:
                continue

            try:
                establishments = (
                    IdentityEstablishment.objects.get_establishments(o.owner)
                )

            except Exception, e:
                logger.exception(e.message)
                continue

            if 1 == len(establishments):
                establishment = establishments[0]

            else:
                establishment = None
                for e in establishments:
                    if e.name == o.owner.name:
                        establishment = e

            if not establishment:
                logger.error(' '.join([
                    'Could not migrate offer belonging to business',
                    o.owner.name
                ]))
                failed_offer_migrations.append({
                    'offer': o,
                    'to': establishment
                })
                continue

            try:
                transactions = Transaction.objects.filter(offer=o)

            except Exception, e:
                logger.exception(e.message)
                failed_offer_migrations.append({
                    'offer': o,
                    'to': establishment
                })
                continue

            for t in transactions:
                if t.owner == o.owner:
                    try:
                        original_owner = t.owner
                        t.owner = establishment
                        t.save()
                        transactions_migrated_total += 1

                        logger.info(''.join([
                            'Migrated transaction: ',
                            t.pk,
                            'from: ',
                            original_owner.name,
                            ' (',
                            str(original_owner.identity_type),
                            ') ',
                            'to: ',
                            t.owner.name,
                            ' (',
                            str(t.owner.identity_type),
                            ') '
                        ]))

                    except Exception, e:
                        logger.exception(e.message)
                        failed_transction_migrations.append({
                            'transaction': t,
                            'to': establishment
                        })

            try:
                original_owner = o.owner
                o.owner = establishment
                o.save()
                offers_migrated_total += 1

                logger.info(''.join([
                    'Migrated offer: ',
                    o.pk,
                    'from: ',
                    original_owner.name,
                    ' (',
                    str(original_owner.identity_type),
                    ') ',
                    'to: ',
                    o.owner.name,
                    ' (',
                    str(o.owner.identity_type),
                    ') '
                ]))

            except Exception, e:
                logger.exception(e.message)
                failed_offer_migrations.append({
                    'offer': o,
                    'to': establishment
                })

        x += chunk_size
        offer_chunk = all_offers[x:x + chunk_size]

    return failed_offer_migrations, failed_transction_migrations


def retry_offer_migrations(failed_offer_migrations):
    failed_again = []

    for m in failed_offer_migrations:
        offer = m.get('offer')
        to = m.get('to')

        if not to:
            failed_again.append(m)
            continue

        try:
            offer.owner = to
            offer.save()

        except Exception, e:
            logger.exception(e.message)
            failed_again.append(m)

    return failed_again


def retry_transaction_migrations(failed_transaction_migrations):
    failed_again = []

    for m in failed_transaction_migrations:
        offer = m.get('transaction')
        to = m.get('to')

        if not to:
            failed_again.append(m)
            continue

        try:
            offer.owner = to
            offer.save()

        except Exception, e:
            logger.exception(e.message)
            failed_again.append(m)

    return failed_again

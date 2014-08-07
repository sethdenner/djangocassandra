from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.identity.models import IdentityTypes


class InvalidMigrationSourceException(Exception):
    message = 'This migration source is not an identity of type "BUSINESS"'


def get_migration_target(business):
    from knotis.contrib.identity.models import IdentityEstablishment

    if IdentityTypes.BUSINESS != business.identity_type:
        raise InvalidMigrationSourceException()

    try:
        establishments = (
            IdentityEstablishment.objects.get_establishments(business)
        )

    except Exception, e:
        logger.exception(e.message)
        return None

    if 1 == len(establishments):
        establishment = establishments[0]

    else:
        establishment = None
        for e in establishments:
            if e.name == business.name:
                establishment = e

    return establishment


def move_inventory_to_establishment():
    from knotis.contrib.inventory.models import Inventory

    all_inventory = Inventory.objects.all()
    failed_inventory_migrations = []
    x = 0
    chunk_size = 20
    inventory_chunk = all_inventory[x:x + chunk_size]

    while len(inventory_chunk):
        for i in inventory_chunk:
            if (
                IdentityTypes.BUSINESS != i.provider.identity_type and
                IdentityTypes.BUSINESS != i.recipient.identity_type
            ):
                continue

            try:
                establishment_provider = get_migration_target(i.provider)

            except InvalidMigrationSourceException:
                pass

            try:
                establishment_recipient = get_migration_target(i.recipient)

            except InvalidMigrationSourceException:
                pass

            if not establishment_provider and not establishment_recipient:
                logger.error(''.join([
                    'Failed to migrate invetory: ',
                    i.pk,
                    '.'
                ]))

                failed_inventory_migrations.append({
                    'inventory': i,
                    'to_provider': establishment_provider,
                    'to_recipient': establishment_recipient
                })
                continue

            original_provider = i.provider
            original_recipient = i.recipient

            if establishment_provider:
                i.provider = establishment_provider

            if establishment_recipient:
                i.recipient = establishment_recipient

            if establishment_recipient or establishment_provider:
                try:
                    i.save()

                    logger.info(''.join([
                        'Migration of inventory ',
                        i.pk,
                        ' from provider: ',
                        original_provider.name,
                        ' (',
                        str(original_provider.identity_type),
                        ') ',
                        ' to provider: ',
                        i.provider.name,
                        ' (',
                        str(i.provider.identity_type),
                        ') ',
                        ' and from recipient: ',
                        original_recipient.name,
                        ' (',
                        str(original_recipient.identity_type),
                        ') ',
                        ' to recipient: ',
                        i.recipient.name,
                        ' (',
                        str(i.recipient.identity_type),
                        ') |Success!'
                    ]))

                except Exception, e:
                    logger.exception(e.message)

        x += chunk_size
        inventory_chunk = all_inventory[x:x + chunk_size]

    return failed_inventory_migrations


def move_offers_to_establishment():
    from knotis.contrib.offer.models import Offer
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

            establishment = get_migration_target(o.owner)

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

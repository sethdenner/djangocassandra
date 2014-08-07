from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.inventory.models import Inventory


def merge_identity_inventory(identity):
    stacked = Inventory.objects.filter(
        provider=identity,
        recipient=identity
    )

    product_set = set()
    for i in stacked:
        product_set |= set([i.product.pk])

    for p in product_set:
        total_stock = 0
        duplicate_inventory = []
        for i in stacked:
            if len(i.offeritem_set.all()):
                continue

            if p == i.product.pk:
                total_stock += i.stock
                duplicate_inventory.append(i)

        if 1 < len(duplicate_inventory):
            logger.info('Found Duplicates')
            save_me = duplicate_inventory.pop()
            merge_count = 1
            for i in duplicate_inventory:
                i.delete()
                merge_count += 1

            save_me.stock = total_stock
            save_me.save()

            logger.info(''.join([
                'Merged ',
                str(merge_count),
                ' inventories of ',
                save_me.product.title,
                ' for ',
                save_me.provider.name,
                '.'
            ]))


def merge_stacked_inventory():
    from knotis.contrib.inventory.models import Identity

    all_identities = Identity.objects.all()
    failed_inventory_merges = []
    x = 0
    chunk_size = 20
    identity_chunk = all_identities[x:x + chunk_size]

    while len(identity_chunk):
        for i in identity_chunk:
            try:
                merge_identity_inventory(i)

            except Exception, e:
                logger.exception(e.message)
                failed_inventory_merges.append({
                    'identity': i,
                    'exception': e
                })

        x += chunk_size
        identity_chunk = all_identities[x:x + chunk_size]

    return failed_inventory_merges

import os
import shutil

from knotis.contrib.media.models import (
    Image,
    ImageInstance
)

from django.core.files.base import ContentFile
from knotis.contrib.offer.models import (
    OfferCollection,
    OfferCollectionItem,
)


def import_images(directory, output_directory, neighborhood):
    passport_images = os.listdir(directory)
    sorted_files = {int(x.strip('.jpg')): x for x in passport_images}

    offer_collection = OfferCollection.objects.get(neighborhood=neighborhood)
    offer_collection_items = OfferCollectionItem.objects.filter(
        offer_collection=offer_collection
    )

    for offer_collection_item, image in zip(
        offer_collection_items,
        sorted_files.values()
    ):
        src = os.path.join(directory, image)
        dst = os.path.join(output_directory, neighborhood + image)
        shutil.copy(src, dst)
        image = Image(
            owner=offer_collection_item.offer.owner,
        )
        image_source = open(dst).read()
        image.image.save(
            dst,
            ContentFile(image_source)
        )
        image.save()

        ImageInstance.objects.create(
            owner=offer_collection_item.offer.owner,
            image=image,
            related_object_id=offer_collection_item.offer.id,
            context='offer_banner',
            primary=True
        )


if __name__ == '__main__':
    import sys
    import_images(*sys.argv[1:])

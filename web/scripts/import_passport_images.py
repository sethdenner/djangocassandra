import os

from knotis.contrib.media.api import (
    ImageApi,
    ImageInstanceApi,
)

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
        image = ImageApi.import_offer_image(src, offer_collection_item.offer)
        ImageInstanceApi.create_offer_image_instance(
            image,
            offer_collection_item.offer
        )


if __name__ == '__main__':
    import sys
    import_images(*sys.argv[1:])

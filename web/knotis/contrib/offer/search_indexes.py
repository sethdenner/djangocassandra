import datetime
from haystack import indexes
from models import (
    Offer,
    OfferCollectionItem
)


class OfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='owner', null=True)
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    # Haystack is busted.
    # https://github.com/django-haystack/django-haystack/issues/866#issuecomment-27708342
    active = indexes.BooleanField(model_attr='active', indexed=False)
    available = indexes.BooleanField(model_attr='available', indexed=False)
    published = indexes.BooleanField(model_attr='published', indexed=False)
    completed = indexes.BooleanField(model_attr='completed', indexed=False)

    location = indexes.LocationField(model_attr='get_location')

    def get_model(self):
        return Offer

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            pub_date__lte=datetime.datetime.now()
        )


class OfferCollectionItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    offer_collection = indexes.CharField(
        model_attr='offer_collection',
        null=True
    )
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    location = indexes.LocationField(model_attr='get_location')

    def get_model(self):
        return OfferCollectionItem

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            pub_date__lte=datetime.datetime.now()
        )

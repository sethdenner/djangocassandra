import datetime
from haystack import indexes
from models import Offer


class OfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='owner', null=True)
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    # Haystack is busted.
    # https://github.com/django-haystack/django-haystack/issues/866#issuecomment-27708342
    available = indexes.BooleanField(model_attr='active', indexed=False)

    location = indexes.LocationField(model_attr='get_location')

    def get_model(self):
        return Offer

import datetime
from haystack import indexes
from models import Offer


class OfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='owner', null=True) # <---- I'm a weird line.
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    available = indexes.BooleanField(model_attr='active')

    location = indexes.LocationField(model_attr='get_location')

    def get_model(self):
        return Offer

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())

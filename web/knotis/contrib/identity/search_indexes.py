import datetime
from haystack import indexes
from models import Identity, IdentityEstablishment


class IdentityIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='name')
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    # Haystack is busted.
    # https://github.com/django-haystack/django-haystack/issues/866#issuecomment-27708342
    available = indexes.BooleanField(model_attr='available', indexed=False)

    location = indexes.LocationField(model_attr='get_location')

    def get_model(self):
        return Identity

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            pub_date__lte=datetime.datetime.now()
        )


class IdentityEstablishmentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='name')
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    available = indexes.BooleanField(model_attr='available', indexed=False)

    location = indexes.LocationField(model_attr='get_location')

    def get_model(self):
        return IdentityEstablishment

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            pub_date__lte=datetime.datetime.now()
        )
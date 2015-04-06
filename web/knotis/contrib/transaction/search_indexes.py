import datetime
from haystack import indexes
from models import Transaction


class TransactionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    # Haystack is busted.
    # https://github.com/django-haystack/django-haystack/issues/866#issuecomment-27708342
    has_redemptions = indexes.BooleanField(
        model_attr='has_redemptions',
        indexed=False
    )

    redemption_code = indexes.EdgeNgramField(model_attr='redemption_code')
    transaction_type = indexes.CharField(model_attr='transaction_type')

    owner = indexes.CharField(model_attr='owner', null=True)
    content_auto = indexes.EdgeNgramField(model_attr='owner')

    def get_model(self):
        return Transaction

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            pub_date__lte=datetime.datetime.now()
        )

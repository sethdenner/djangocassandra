from knotis.forms import ModelForm
from models import Offer


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = (
            'content_type',
            'delete'
        )

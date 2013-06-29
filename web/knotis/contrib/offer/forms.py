from django.forms import (
    Form,
    ModelForm,
    CharField,
    FloatField,
    IntegerField,
    BooleanField,
    ModelChoiceField,
    RadioSelect
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Div,
    Field
)

from models import Offer


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = (
            'content_type',
            'delete'
        )


class OfferProductPriceForm(Form):
    product_type = CharField(
        max_length=16,
        widget=RadioSelect(
            choices=(
                'credit', 'Credit',
                'physical', 'Physical',
                'previous', 'Previous'
            )
        ),
        label=''
    )

    previous_offers = ModelChoiceField(
        queryset=Offer.objects.filter(),
        empty_label='Previous Offers',
        label=''
    )

    credit_price = FloatField(
        label='',
        required=False
    )
    credit_value = FloatField(
        label='',
        required=False
    )

    product_title = CharField(
        label='',
        max_length=140,
        required=False
    )
    product_price = FloatField(
        label='',
        required=False
    )
    product_value = FloatField(
        label='',
        required=False
    )

    offer_stock = IntegerField(
        label='',
        required=False
    )
    offer_unlimited = BooleanField(
        label='',
        required=False
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(OfferProductPriceForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-offer-product-price-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                'product_type',
                Div(
                    'credit_price',
                    'credit_value',
                    css_class='controls'
                ),
                css_class='control-group'
            )
        )


class OfferDetailsForm(OfferForm):
    class Meta(OfferForm.Meta):
        fields = (
            'title',
            'description',
            'restrictions'
        )


class OfferPhotoLocationForm(Form):
    pass


class OfferPublicationForm(Form):
    pass


class OfferWithInventoryForm(OfferForm):
    class Meta(OfferForm.Meta):
        pass

    inventory_0 = CharField(
        max_length=36
    )

    discount_factor = FloatField()

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(OfferWithInventoryForm, self).__init__(
            *args,
            **kwargs
        )

        data = kwargs.get('data')

        for count in range(1, 100):
            key = 'inventory_' + count
            if data.get(key):
                self.fields[key] = CharField(
                    max_length=36,
                )

            else:
                break

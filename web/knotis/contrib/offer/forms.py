from django.forms import (
    Form,
    ModelForm,
    CharField,
    FloatField,
    IntegerField,
    BooleanField,
    ModelChoiceField,
    RadioSelect,
    HiddenInput
)

from knotis.contrib.identity.models import Identity

from models import Offer


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = (
            'content_type',
            'delete'
        )


class OfferProductPriceForm(Form):
    template = 'knotis/offer/create_product_price.html'
    form_id = 'id-offer-product-price'
    form_method = 'POST'
    form_action = '/offer/create/product/'

    owner = ModelChoiceField(
        widget=HiddenInput(),
        queryset=Identity.objects.none()
    )

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
        owners = kwargs.pop('owners')

        super(OfferProductPriceForm, self).__init__(
            *args,
            **kwargs
        )

        self.fields['owner'].queryset = owners


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

from django.forms import (
    Form,
    ModelForm,
    CharField,
    FloatField,
    IntegerField,
    BooleanField,
    ModelChoiceField,
    RadioSelect,
    HiddenInput,
    ValidationError
)

from knotis.contrib.identity.models import Identity
from knotis.contrib.product.models import ProductTypes

from models import Offer


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = (
            'content_type',
            'delete'
        )


class OfferProductPriceForm(Form):
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

        if owners:
            self.fields['owner'].queryset = owners

        if not hasattr(self, 'POST'):
            return

        product_type = self.POST.get('product_type')
        if product_type == ProductTypes.CREDIT:
            self.fields['credit_price'].required = True
            self.fields['credit_value'].required = True

        elif product_type == ProductTypes.PHYSICAL:
            self.fields['product_title'].required = True
            self.fields['product_price'].required = True
            self.fields['product_value'].required = True

        if not self.POST.get('unlimited'):
            self.fields['offer_stock'].required = True

    def clean(self):
        cleaned_data = super(OfferProductPriceForm, self).clean()

        product_type = cleaned_data.get('product_type')
        if ProductTypes.CREDIT == product_type:
            price = cleaned_data.get('credit_price')
            value = cleaned_data.get('credit_value')

        elif ProductTypes.PHYSICAL == product_type:
            price = cleaned_data.get('product_price')
            value = cleaned_data.get('product_value')

        else:
            raise ValidationError(
                'only credit and physical products '
                'can be created by this form.'
            )

        if price > value:
            raise ValidationError(
                'discount price must be less than retail price.'
            )

        return cleaned_data


class OfferDetailsForm(OfferForm):
    class Meta(OfferForm.Meta):
        fields = (
            'title',
            'description',
            'restrictions'
        )

    form_id = 'id-offer-details'
    form_method = 'POST'
    form_action = '/offer/create/details/'


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

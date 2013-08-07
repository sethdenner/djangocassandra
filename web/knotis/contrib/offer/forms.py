from django.forms import (
    Form,
    ModelForm,
    CharField,
    FloatField,
    IntegerField,
    BooleanField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    RadioSelect,
    HiddenInput,
    ValidationError
)

from knotis.forms import (
    TemplateForm,
    ItemSelectWidget,
    ItemSelectRow,
    ItemSelectAction
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.product.models import ProductTypes
from knotis.contrib.location.models import Location
from knotis.contrib.media.models import Image

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


class OfferPhotoLocationForm(TemplateForm):
    template_name = 'knotis/offer/offer_photo_location_form.html'
    form_action = '/offer/create/location/'
    form_id = 'offer_photo_location_form'
    form_method = 'POST'

    offer = ModelChoiceField(
        queryset=Offer.objects.none(),
        widget=HiddenInput()
    )

    photo = ModelChoiceField(
        queryset=Image.objects.none(),
        widget=ItemSelectWidget(
            render_images=True,
            image_dimensions='32x32'
        )
    )

    locations = ModelMultipleChoiceField(
        queryset=Location.objects.none(),
        widget=ItemSelectWidget(select_multiple=True)
    )

    def __init__(
        self,
        offer=None,
        photos=None,
        locations=None,
        *args,
        **kwargs
    ):
        super(OfferPhotoLocationForm, self).__init__(
            *args,
            **kwargs
        )

        if offer:
            self.fields['offer'].queryset = Offer.objects.filter(**{
                'pk__in': [offer.id]
            })
            self.fields['offer'].initial = offer

        if photos:
            self.fields['photo'].queryset = photos

            rows = [
                ItemSelectRow(
                    photo,
                    image=photo.image
                ) for photo in photos
            ]
            actions = [
                ItemSelectAction(
                    'Crop',
                    '#crop-image',
                    'anchor-green'
                ),
                ItemSelectAction(
                    'Delete',
                    '#delete-image',
                    'anchor-red',
                    method='DELETE'
                )
            ]

            if rows:
                rows[0].checked = True

            photo_widget = self.fields['photo'].widget
            photo_widget.rows = rows
            photo_widget.actions = actions

        if locations:
            self.fields['locations'].queryset = locations

            rows = [
                ItemSelectRow(
                    location,
                    title=location.address,
                    checked=True
                ) for location in locations
            ]
            actions = [
                ItemSelectAction(
                    'Edit Location',
                    '#edit-location'
                )
            ]

            locations_widget = self.fields['locations'].widget
            locations_widget.rows = rows
            locations_widget.actions = actions


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

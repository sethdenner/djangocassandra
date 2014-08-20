from django.forms import (
    Form,
    CharField,
    FloatField,
    IntegerField,
    BooleanField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    DateTimeField,
    RadioSelect,
    HiddenInput,
    ValidationError
)


from knotis.forms import (
    TemplateForm,
    ModelForm,
    ItemSelectWidget,
    ItemSelectRow,
    ItemSelectAction
)
from knotis.contrib.identity.models import Identity
from knotis.contrib.product.models import ProductTypes
from knotis.contrib.location.models import Location
from knotis.contrib.media.models import (
    Image,
    ImageInstance
)
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)

from knotis.contrib.offer.models import (
    Offer,
    OfferItem,
    OfferPublish
)

from knotis.contrib.offer.forms import OfferForm


class OfferFinishForm(OfferForm):
    form_action = '/offer/create/summary/'
    form_method = 'POST'

    id = CharField(widget=HiddenInput)

    class Meta(OfferForm.Meta):
        fields = (
            'id',
            'published'
        )
        exclude = ()
        widgets = {
            'published': HiddenInput()
        }

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(OfferFinishForm, self).__init__(
            *args,
            **kwargs
        )

        self.initial['published'] = True

    def save(
        self,
        *args,
        **kwargs
    ):
        # Don't actually want to update instance
        # here Offer will get publish set to True
        # when publish_offers script is run.
        instance = super(OfferFinishForm, self).save(
            commit=False,
            *args,
            **kwargs
        )

        if instance.published:
            offer_publish = OfferPublish.objects.filter(
                subject_object_id=instance.id
            )

            for publish in offer_publish:
                publish.publish_now = True
                publish.save()

        return instance


class OfferProductPriceForm(Form):
    form_id = 'id-offer-product-price'
    form_method = 'POST'
    form_action = '/offer/create/product/'

    owner = ModelChoiceField(
        widget=HiddenInput(),
        queryset=Identity.objects.none()
    )

    offer_id = CharField(
        max_length=36,
        widget=HiddenInput(),
        required=False
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
        owners = kwargs.pop('owners', None)
        offer = kwargs.pop('offer', None)

        super(OfferProductPriceForm, self).__init__(
            *args,
            **kwargs
        )

        if owners:
            self.fields['owner'].queryset = owners

        if offer:
            self.fields['offer_id'].initial = offer.pk
            offer_item = OfferItem.objects.get(
                offer=offer
            )
            product_type = offer_item.inventory.product.product_type
            self.fields['product_type'].initial = product_type
            stock = offer_item.inventory.stock
            if ProductTypes.CREDIT == product_type:
                self.fields['credit_price'].initial = (
                    offer_item.price_discount * stock
                )
                self.fields['credit_value'].initial = (
                    offer_item.inventory.price * stock
                )

            elif ProductTypes.PHYSICAL == product_type:
                self.fields['product_title'].initial = (
                    offer_item.inventory.product.title
                )

                self.fields['product_price'].initial = (
                    offer_item.price_discount * stock
                )
                self.fields['product_value'].initial = (
                    offer_item.inventory.price * stock
                )

            self.fields['offer_stock'].initial = offer.stock
            self.fields['offer_unlimited'].initial = offer.unlimited

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

    def clean_offer_id(self):
        offer_id = self.cleaned_data.get('offer_id')
        if offer_id:
            Offer.objects.get(pk=offer_id)

        return offer_id

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

        unlimited = cleaned_data.get('offer_unlimited')
        stock = cleaned_data.get('offer_stock')

        if not unlimited and not stock:
            raise ValidationError(
                'Offers must have a quantity or be unlimited'
            )

        return cleaned_data


class OfferDetailsForm(OfferForm):
    class Meta(OfferForm.Meta):
        fields = (
            'id',
            'title',
            'description',
            'restrictions'
        )
        exclude = ()

    form_id = 'id-offer-details'
    form_method = 'POST'
    form_action = '/offer/create/details/'

    id = CharField(widget=HiddenInput())


class OfferPhotoLocationForm(TemplateForm):
    template_name = 'knotis/merchant/offer_photo_location_form.html'
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
        widget=ItemSelectWidget(select_multiple=True),
        required=False
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
                    image=photo
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

    def clean_photo(self):
        offer = self.cleaned_data.get('offer')
        photo = self.cleaned_data.get('photo')

        if photo.related_object_id == offer.id:
            instance = photo
            instance.primary = True
            instance.save()

        else:
            instance = ImageInstance.objects.create(
                owner=offer.owner,
                image=photo.image,
                related_object_id=offer.id,
                crop_left=photo.crop_left,
                crop_top=photo.crop_top,
                crop_width=photo.crop_width,
                crop_height=photo.crop_height,
                context=photo.context,
                primary=True
            )

        return instance


class OfferPublishForm(ModelForm):
    class Meta:
        model = OfferPublish
        exclude = (
            'content_type'
        )


class OfferPublicationForm(TemplateForm):
    template_name = 'knotis/merchant/offer_publish_form.html'
    form_action = '/offer/create/publish/'
    form_id = 'offer_publish_form'
    form_method = 'POST'

    offer = ModelChoiceField(
        queryset=Offer.objects.none(),
        widget=HiddenInput()
    )

    start_time = DateTimeField()
    end_time = DateTimeField(
        required=False,
    )
    no_time_limit = BooleanField(
        required=False
    )

    publish = ModelMultipleChoiceField(
        queryset=Endpoint.objects.none(),
        widget=ItemSelectWidget(select_multiple=True),
        required=False
    )

    def __init__(
        self,
        offer=None,
        publish_queryset=None,
        *args,
        **kwargs
    ):
        super(OfferPublicationForm, self).__init__(
            *args,
            **kwargs
        )

        if offer:
            self.fields['offer'].queryset = Offer.objects.filter(**{
                'pk__in': [offer.id]
            })
            self.fields['offer'].initial = offer
            self.fields['start_time'].initial = offer.start_time
            self.fields['end_time'].initial = offer.end_time
            self.fields['no_time_limit'].initial = (
                offer.start_time and not offer.end_time
            )

        (
            endpoint_facebook,
            endpoint_twitter,
            endpoint_widget,
            endpoint_followers
        ) = None, None, None, None

        if publish_queryset:
            self.fields['publish'].queryset = publish_queryset

            for endpoint in publish_queryset:
                if (
                    not endpoint_facebook and
                    EndpointTypes.FACEBOOK == endpoint.endpoint_type
                ):
                    endpoint_facebook = endpoint

                elif (
                    not endpoint_twitter and
                    EndpointTypes.TWITTER == endpoint.endpoint_type
                ):
                    endpoint_twitter = endpoint

                elif (
                    not endpoint_widget and
                    EndpointTypes.WIDGET == endpoint.endpoint_type
                ):
                    endpoint_widget = endpoint

                elif (
                    not endpoint_followers and
                    EndpointTypes.FOLLOWERS == endpoint.endpoint_type
                ):
                    endpoint_followers = endpoint

        publish_widget = self.fields['publish'].widget
        publish_values = publish_widget.value_from_datadict(
            self.data,
            {},
            'publish'
        )

        rows = [
            ItemSelectRow(
                endpoint_facebook,
                title=(
                    'Facebook' if endpoint_facebook is None else
                    endpoint_facebook.value + ' (Facebook)'
                ),
                checked=(
                    True if endpoint_facebook and endpoint_facebook.pk in
                    publish_values else False
                ),
                disabled=True if endpoint_facebook is None else False,
                action=ItemSelectAction(
                    name='Edit',
                    url='/settings/social/'
                )
            ),
            ItemSelectRow(
                endpoint_twitter,
                title=(
                    'Twitter' if endpoint_twitter is None else
                    endpoint_twitter.value + ' (Twitter)'
                ),
                checked=(
                    True if endpoint_twitter and endpoint_twitter.pk in
                    publish_values else False
                ),
                disabled=True if endpoint_twitter is None else False,
                action=ItemSelectAction(
                    name='Edit',
                    url='/settings/social/'
                )
            ),
            ItemSelectRow(
                endpoint_followers,
                title='Email Followers',
                checked=(
                    True if endpoint_followers and endpoint_followers.pk in
                    publish_values else not publish_values
                ),
                disabled=True if endpoint_followers is None else False,
                action=ItemSelectAction(
                    name='Edit',
                    url='/my/following/'
                )
            )
        ]

        publish_widget = self.fields['publish'].widget
        publish_widget.rows = rows

    def clean(self):
        cleaned_data = self.cleaned_data
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        no_time_limit = cleaned_data.get('no_time_limit')

        if not no_time_limit:
            if start_time >= end_time:
                raise ValidationError('start time must be before end time')

        return cleaned_data


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

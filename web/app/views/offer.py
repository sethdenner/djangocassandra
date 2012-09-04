from django.shortcuts import render  # , redirect
from django.forms import ModelForm, CharField, ImageField
from app.models.offers import Offer
from app.models.businesses import Business
from app.models.endpoints import Endpoint, EndpointAddress
from app.models.images import Image

from app.utils import View as ViewUtils


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = (
            'establishment',
            'offer_type',
            'title',
            'description',
            'restrictions',
            'address',
            'image',
            'purchased',
            'published',
            'pub_date'
        )

    title_value = CharField(max_length=128, initial='Food and Drinks')
    description_value = CharField(max_length=1024)
    restrictions_value = CharField(max_length=1024)
    address_value = CharField(max_length=256)

    image_source = ImageField('/uploads/offers/')

    def save_offer(
        self,
        request
    ):
        business = Business.objects.get(user=request.user)[0]

        address = EndpointAddress(
            type=Endpoint.EndpointTypes.ADDRESS,
            user=request.user,
            value=self.cleaned_data['address_value'],
            primary=True,
        )

        image = Image(
            self.cleaned_data['image_source']
        )
        image.save()

        published = 'Publish' in request.POST

        Offer.objects.create_offer(
            request.user,
            business,
            self.cleaned_data['title_value'],
            self.cleaned_data['title_type'],
            self.cleaned_data['description_value'],
            self.cleaned_data['restrictions_value'],
            self.cleaned_data['city'],
            self.cleaned_data['neighborhood'],
            address,
            image,
            self.cleaned_data['category'],
            self.cleaned_data['price_retail'],
            self.cleaned_data['price_discount'],
            self.cleaned_data['start_date'],
            self.cleaned_data['end_date'],
            self.cleaned_data['stock'],
            self.cleaned_data['unlimited'],
            published
        )


def offers(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'offers.html',
        template_parameters
    )


def create(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            try:
                form.save_offer(request)
                # redirect
            except Exception:
                pass
    else:
        form = OfferForm()

    template_parameters['offer_form'] = form

    return render(
        request,
        'create_offer.html',
        template_parameters
    )

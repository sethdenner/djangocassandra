from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.forms import ModelForm, CharField, ImageField, DateTimeField
from app.models.offers import Offer, OfferStatus
from app.models.businesses import Business
from app.models.categories import Category
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from app.models.users import UserProfile

from app.utils import View as ViewUtils
from app.views.business import edit_profile


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
            'status',
            'purchased',
            'redeemed',
            'published',
            'active',
            'pub_date'
        )

    title_value = CharField(max_length=128, initial='Food and Drinks')
    description_value = CharField(max_length=1024, initial='Description')
    restrictions_value = CharField(max_length=1024, initial='Restrictions')
    address_value = CharField(max_length=256)
    start_date = DateTimeField(initial='Start Date')
    end_date = DateTimeField(initial='End Date')
    image_source = ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if None != instance:
            self.fields['description_value'].initial = instance.description.value
            self.fields['title_value'].initial = instance.title.value
            self.fields['restrictions_value'].initial = instance.restrictions.value
            self.fields['address_value'].initial = instance.address.value.value
            self.fields['neighborhood'].initial = instance.neighborhood

    def save_offer(
        self,
        request,
        offer=None
    ):
        business = Business.objects.get(user=request.user)

        published = 'publish' in request.POST

        if offer:
            offer.update(
                self.cleaned_data['title_value'],
                self.cleaned_data['title_type'],
                self.cleaned_data['description_value'],
                self.cleaned_data['restrictions_value'],
                self.cleaned_data['city'],
                self.cleaned_data['neighborhood'],
                self.cleaned_data['address_value'],
                self.cleaned_data['image_source'],
                self.cleaned_data['category'],
                self.cleaned_data['price_retail'],
                self.cleaned_data['price_discount'],
                self.cleaned_data['start_date'],
                self.cleaned_data['end_date'],
                self.cleaned_data['stock'],
                self.cleaned_data['unlimited'],
                published,
                OfferStatus.CURRENT if published else None,
                active=published
            )
        else:
            Offer.objects.create_offer(
                request.user,
                business,
                self.cleaned_data['title_value'],
                self.cleaned_data['title_type'],
                self.cleaned_data['description_value'],
                self.cleaned_data['restrictions_value'],
                self.cleaned_data['city'],
                self.cleaned_data['neighborhood'],
                self.cleaned_data['address_value'],
                self.cleaned_data['image_source'],
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
    template_parameters['current_page'] = 'offers'

    return render(
        request,
        'offers.html',
        template_parameters
    )


@login_required
def dashboard(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    template_parameters['user_profile'] = UserProfile.objects.get(user=request.user)
    business = Business.objects.get(user=request.user)
    template_parameters['business'] = business
    template_parameters['offers'] = Offer.objects.filter(business=business)

    return render(
        request,
        'offers_dashboard.html',
        template_parameters
    )


@login_required
def edit(request, offer_id=None):
    try:
        Business.objects.get(user=request.user)
    except:
        return redirect(edit_profile)

    offer = None
    if None != offer_id:
        try:
            offer = Offer.objects.get(pk=offer_id)
        except:
            pass

    feedback = None
    if request.method == 'POST':
        form = OfferForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            try:
                form.save_offer(request, offer)
                return redirect('/offers/dashboard/')
            except ValueError as e:
                feedback = 'ValueError: ' + e.message
            except Exception as e:
                feedback = 'UnexpectedError: ' + e.message
        else:
            feedback = 'The following fields are invalid: '
            for error in form.errors:
                feedback += strip_tags(error) + '<br/>'
    else:
        form = OfferForm(instance=offer)


    template_parameters = ViewUtils.get_standard_template_parameters(request)

    if offer:
        template_parameters['neighborhoods'] = Neighborhood.objects.filter(city=offer.city)

    template_parameters['business'] = Business.objects.get(user=request.user)
    template_parameters['categories'] = Category.objects.all()
    template_parameters['cities'] = City.objects.all()
    template_parameters['offer_form'] = form
    template_parameters['offer'] = offer
    template_parameters['feedback'] = feedback

    return render(
        request,
        'create_offer.html',
        template_parameters
    )

def get_offers_by_status(
    request,
    status
):
    template_parameters = {}
    template_parameters['offers'] = Offer.objects.filter(status=status)
    try:
        template_parameters['user_profile'] = UserProfile.objects.get(user=request.user)
        template_parameters['business'] = Business.objects.get(user=request.user)
    except:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )

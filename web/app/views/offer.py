from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.http import HttpResponse, HttpResponseBadRequest
from django.forms import ModelForm, CharField, ImageField, DateTimeField
from app.models.offers import Offer, OfferStatus
from app.models.businesses import Business
from app.models.categories import Category
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from knotis_auth.models import UserProfile

from app.utils import View as ViewUtils
from app.views.business import edit_profile

from pymaps.pymaps import PyMap


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
            self.fields['description_value'].initial = \
                instance.description.value
            self.fields['title_value'].initial = instance.title.value
            self.fields['restrictions_value'].initial = \
                instance.restrictions.value
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

    try:
        template_parameters['offers'] = Offer.objects.get_newest_offers()
        template_parameters['offers_premium'] = \
            Offer.objects.get_premium_offers()
    except:
        pass
    template_parameters['offer_load_uri'] = '/offers/get_newest_offers/'
    template_parameters['offer_load_context'] = ''

    try:
        template_parameters['categories'] = Category.objects.all()
        template_parameters['total_active_offers'] = \
            Offer.objects.get_active_offer_count()
    except:
        pass

    gmap = PyMap()
    gmap.key = settings.GOOGLE_MAPS_API_KEY
    template_parameters['map_script'] = gmap.headerjs()

    return render(
        request,
        'offers.html',
        template_parameters
    )


def offer(
    request,
    offer_id
):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    try:
        template_parameters['offer'] = Offer.objects.get(pk=offer_id)
    except:
        redirect(offers)

    try:
        template_parameters['categories'] = Category.objects.all()
        template_parameters['total_active_offers'] = \
            Offer.objects.get_active_offer_count()
    except:
        pass

    gmap = PyMap()
    gmap.key = settings.GOOGLE_MAPS_API_KEY
    template_parameters['map_script'] = gmap.headerjs()
    template_parameters['BASE_URL'] = settings.BASE_URL

    return render(
        request,
        'offer.html',
        template_parameters
    )


@login_required
def dashboard(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    business = None
    try:
        business = Business.objects.get(user=request.user)
        template_parameters['business'] = business
    except:
        pass

    if business:
        offers = None
        try:
            template_parameters['offers'] = Offer.objects.filter(
                business=business,
                status=OfferStatus.CREATED
            )
        except:
            pass

    template_parameters['user_profile'] = UserProfile.objects.get(
        user=request.user
    )

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

    template_parameters['cities'] = cities = City.objects.all()
    template_parameters['cities'] = cities

    if offer and offer.city:
        template_parameters['neighborhoods'] = Neighborhood.objects.filter(
            city=offer.city
        )
    elif len(cities):
        template_parameters['neighborhoods'] = Neighborhood.objects.filter(
            city=cities[0]
        )
    else:
        template_parameters['neighborhoods'] = None

    template_parameters['business'] = Business.objects.get(user=request.user)
    template_parameters['categories'] = Category.objects.all()
    template_parameters['offer_form'] = form
    template_parameters['offer'] = offer
    template_parameters['feedback'] = feedback

    return render(
        request,
        'create_offer.html',
        template_parameters
    )


def update(request):
    if request.method.lower() != 'post':
        return HttpResponseBadRequest()

    offer = None
    offer_id = request.POST.get('offer_id')
    active = ViewUtils.get_boolean_from_request(
        request,
        'active'
    )

    try:
        offer = Offer.objects.get(pk=offer_id)
    except:
        pass

    if not offer:
        return HttpResponseBadRequest()

    try:
        offer.update(
            active=active
        )
    except:
        pass

    return HttpResponse()


def get_category_offers(
    request,
    category_short_name,
    city_name=None,
    neighborhood_name=None,
    page='1'
):
    template_parameters = {}

    if category_short_name.strip().lower() == 'all':
        template_parameters['offers'] = Offer.objects.get_newest_offers(
            page=int(page) if page else 1
        )
    else:
        categories = None
        try:
            categories = Category.objects.all()
        except:
            pass

        if not categories:
            return None

        the_category = None
        for category in categories:
            if category_short_name == category.short_name():
                the_category = category
                break

        try:
            template_parameters['offers'] = Offer.objects.get_category_offers(
                category=the_category,
                page=int(page) if page else 1
            )
        except:
            pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def get_popular_offers(
    request,
    city_name=None,
    neighborhood_name=None,
    page='1'
):
    template_parameters = {}
    try:
        template_parameters['offers'] = Offer.objects.get_popular_offers(
            city_name,
            neighborhood_name,
            page=int(page) if page else 1
        )
    except:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def get_newest_offers(
    request,
    city_name=None,
    neighborhood_name=None,
    page='1'
):
    template_parameters = {}
    try:
        template_parameters['offers'] = Offer.objects.get_newest_offers(
            city_name,
            neighborhood_name,
            page=int(page) if page else 1
        )
    except:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def get_expiring_offers(
    request,
    city_name=None,
    neighborhood_name=None,
    page='1'
):
    template_parameters = {}
    try:
        template_parameters['offers'] = Offer.objects.get_expiring_offers(
            city_name,
            neighborhood_name,
            page=int(page) if page else 1
        )
    except:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def get_offers_by_status(
    request,
    status,
    business_id=None,
    page='1'
):
    template_parameters = {}
    try:
        template_parameters['user_profile'] = UserProfile.objects.get(
            user=request.user
        )

        business = None
        if business_id:
            business = business.objects.get(
                pk=business_id
            )
        else:
            business = Business.objects.get(
                user=request.user
            )
        template_parameters['business'] = business

        template_parameters['offers'] = Offer.objects.filter(
            status=status,
            business=business,
            page=int(page) if page else 1
        )

    except:
        pass

    return render(
        request,
        'offers_list_manage.html',
        template_parameters
    )


def get_available_offers(
    request,
    business_name=None,
    city_name=None,
    neighborhood_name=None,
    category_short_name=None,
    page='1'
):
    template_parameters = {}

    try:
        business = None
        if business_name:
            business = Business.objects.get(backend_name=business_name)

        city = None
        if city_name:
            city = City.objects.get(name_denormalized=city_name)

        neighborhood = None
        if neighborhood_name:
            neighborhood = \
                Neighborhood.objects.get(name_denormalized=neighborhood_name)

        category = None
        if category_short_name:
            category = Category.objects.get(name_short=category_short_name)

        template_parameters['offers'] = Offer.objects.get_available_offers(
            business=business,
            city=city,
            neighborhood=neighborhood,
            category=category,
            page=page
        )
    except:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def search_offers(
    request,
    query
):
    template_parameters = {}

    try:
        template_parameters['offers'] = Offer.objects.search_offers(query)
    except:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def offer_map(request):
    template_parameters = {}

    try:
        template_parameters['offers'] = \
            Offer.objects.get_available_offers()
    except:
        pass

    return render(
        request,
        'offer_map.html',
        template_parameters
    )

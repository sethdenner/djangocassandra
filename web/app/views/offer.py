from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseServerError
from django.forms import ModelForm, CharField, ImageField, DateTimeField, \
    ValidationError
from app.models.offers import Offer, OfferStatus, OfferSort, OfferTitleTypes
from app.models.businesses import Business, BusinessSubscription
from app.models.transactions import Transaction, TransactionTypes
from app.models.categories import Category
from app.models.cities import City
from app.models.neighborhoods import Neighborhood
from app.models.media import Image

from knotis_auth.models import User, UserProfile

from app.utils import View as ViewUtils
from app.views.business import edit_profile

from knotis_maps.views import OfferMap
from paypal.views import generate_ipn_hash, render_paypal_button


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
            'last_purchase',
            'pub_date',
        )

    title_value = CharField(max_length=128, required=False)
    description_value = CharField(max_length=1024)
    restrictions_value = CharField(max_length=1024)
    address_value = CharField(max_length=256)
    start_date = DateTimeField()
    end_date = DateTimeField()
    image_source = ImageField(required=False)
    neighborhood = CharField(max_length=128, required=False)
    city = CharField(max_length=128)

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(OfferForm, self).__init__(
            *args,
            **kwargs
        )

        instance = kwargs.get('instance')
        if None != instance:
            self.fields['description_value'].initial = \
                instance.description.value
            self.fields['title_value'].initial = instance.title.value
            self.fields['restrictions_value'].initial = \
                instance.restrictions.value
            self.fields['address_value'].initial = instance.address.value.value
            self.fields['neighborhood'].initial = instance.neighborhood.id if instance.neighborhood else None
            self.fields['city'].initial = instance.city.id if instance.city else None

    def clean_title_value(self):
        title = self.cleaned_data.get('title_value')
        title_type = self.cleaned_data.get('title_type')

        if not title and title_type != OfferTitleTypes.TITLE_1:
            raise ValidationError('Invalid title.')

        return title

    def clean_city(self):
        try:
            self.cleaned_data['city'] = City.objects.get(pk=self.cleaned_data['city'])

        except:
            raise ValidationError('Invalid city.')

        return self.cleaned_data['city']

    def clean_neighborhood(self):
        neighborhood = self.cleaned_data.get('neighborhood')
        if neighborhood and '-1' != neighborhood:
            try:
                self.cleaned_data['neighborhood'] = Neighborhood.objects.get(pk=neighborhood)

            except:
                raise ValidationError('Invalid neighborhood')

        else:
            self.cleaned_data['neighborhood'] = None

        return self.cleaned_data['neighborhood']

    def clean_unlimited(self):
        unlimited = self.data.get('unlimited')
        self.cleaned_data['unlimited'] = unlimited != None
        return self.cleaned_data['unlimited']

    def save_offer(
        self,
        request,
        offer=None
    ):
        business = Business.objects.get(user=request.user)

        published = offer.published if offer else False
        published = published or 'publish' in request.POST

        if published and not self.cleaned_data.get('image_source'):
            if offer:
                try:
                    offer_images = Image.objects.filter(related_object_id=offer.id)
                except:
                    offer_images = None
            else:
                offer_images = None

            if not offer_images:
                raise ValidationError(
                    'Offer image is required before publishing.'
                )

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


def offers(
    request,
    business=None,
    category=None,
    premium=None,
    page='1',
    sort_by=OfferSort.NEWEST
):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    template_parameters['current_page'] = 'offers'

    city = request.GET.get('city')
    if city:
        if city.lower() == 'all':
            request.session.pop(
                'city',
                None
            )
            request.session.pop(
                'neighborhood',
                None
            )

        else:
            request.session['city'] = city

        neighborhood = request.GET.get('neighborhood')
        if neighborhood:
            if neighborhood.lower() == 'all':
                request.session.pop(
                    'neighborhood',
                    None
                )

            else:
                request.session['neighborhood'] = neighborhood
        else:
            request.session.pop(
                'neighborhood',
                None
            )

    try:
        business_instance = None
        if business:
            business_instance = Business.objects.get(
                backend_name=business.lower()
            )

        neighborhood_instance = None
        if request.session.has_key('neighborhood'):
            neighborhood = request.session.get('neighborhood')
            neighborhood_instance = Neighborhood.objects.get(
                name_denormalized=neighborhood.title()
            )

        city_instance = None
        if request.session.has_key('city'):
            city = request.session.get('city')
            city_instance = City.objects.get(name_denormalized=city.title())

        category_instance = None
        if category:
            category_instance = Category.objects.get(
                name_short=category.lower()
            )
            template_parameters['category'] = category

        query = request.GET.get('query')
        if query:
            template_parameters['query'] = query

        template_parameters['offers'] = Offer.objects.get_available_offers(
            business_instance,
            city_instance,
            neighborhood_instance,
            category_instance,
            premium,
            int(page) if page else 1,
            query,
            sort_by.lower()
        )

        template_parameters['offers_premium'] = \
            Offer.objects.get_available_offers(
                premium=True,
                page=1,
                sort_by=OfferSort.NEWEST
            )[:5]

    except Exception as e:
        pass

    template_parameters['load_offers_href'] = '/offers/get_newest_offers/'
    template_parameters['load_offers_query'] = ''
    template_parameters['load_offers_business'] = ''
    template_parameters['load_offers_city'] = ''
    template_parameters['load_offers_neighborhood'] = ''
    template_parameters['load_offers_category'] = ''
    template_parameters['load_offers_premium'] = ''
    template_parameters['load_offers_page'] = '1'

    try:
        template_parameters['categories'] = Category.objects.all()
        template_parameters['total_active_offers'] = \
            Offer.objects.get_active_offer_count()

    except:
        pass

    offer_map = OfferMap(
        settings.GOOGLE_MAPS_API_KEY,
        template_parameters.get('offers')
    )
    template_parameters['google_map_api_script'] = offer_map.render_api_js()

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

    offer = None
    try:
        offer = Offer.objects.get(pk=offer_id)
        template_parameters['offer'] = offer

    except:
        redirect(offers)

    if not request.user.is_anonymous():
        try:
            subscription = BusinessSubscription.objects.get(
                business=offer.business,
                user=request.user
            )
            template_parameters['is_following'] = \
                None != subscription and subscription.active

        except Exception, e:
            pass

    try:
        template_parameters['categories'] = Category.objects.all()
        template_parameters['total_active_offers'] = \
            Offer.objects.get_active_offer_count()
    except:
        pass

    offer_map = OfferMap(
        settings.GOOGLE_MAPS_API_KEY,
        [template_parameters['offer']]
    )
    template_parameters['google_map_api_script'] = offer_map.render_api_js()
    template_parameters['map_script'] = offer_map.render()
    template_parameters['BASE_URL'] = settings.BASE_URL
    template_parameters['gallery'] = True

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
def print_unredeemed(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    try:
        business = Business.objects.get(user=request.user)

        template_parameters['business'] = business

        offers = Offer.objects.filter(
            business=business
        )

        purchases = Transaction.objects.filter(
            business=business,
            transaction_type=TransactionTypes.PURCHASE
        )

        offer_purchase_map = {}
        for offer in offers:
            offer_purchase_map[offer] = []
            for purchase in purchases:
                if purchase.offer == offer:
                    offer_purchase_map[offer].append(purchase)

        template_parameters['offer_purchase_map'] = offer_purchase_map

    except:
        pass

    return render(
        request,
        'print_unredeemed_offers.html',
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

            except ValueError, e:
                feedback = 'ValueError: ' + e.message

            except ValidationError, e:
                feedback = 'The following fields are invalid:'
                for message in e.messages:
                    feedback = '<br/>'.join([
                        feedback,
                        message
                    ])

            except Exception, e:
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
    template_parameters['scripts'] = [
        'views/offer.edit.js'
    ]

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


@login_required
def delete_offer(
    request,
    offer_id
):
    if request.method.lower() != 'post':
        return HttpResponseBadRequest('Method needs to be POST')

    try:
        offer = Offer.objects.get(pk=offer_id)
    except:
        offer = None

    if not offer:
        return HttpResponseNotFound('Offer does not exist.')

    if offer.business.user_id != request.user.id:
        return HttpResponseBadRequest(
            'Offer does not belong to logged in user.'
        )

    try:
        offer.delete()
    except Exception, error:
        return HttpResponseServerError(error.message)

    return HttpResponse('OK')


@login_required
def get_user_offers(
    request,
    status
):
    template_parameters = {}

    try:
        template_parameters['user_profile'] = UserProfile.objects.get(
            user=request.user
        )

    except:
        pass

    try:
        if status == 'redeemed':
            transaction_type = TransactionTypes.REDEMPTION

        elif status == 'purchased':
            transaction_type = TransactionTypes.PURCHASE

        else:
            transaction_type = None

        transactions = Transaction.objects.filter(
            user=request.user,
            transaction_type=transaction_type
        )

        template_parameters['offers'] = [{
                'id': transaction.offer_id,
                'available': transaction.offer.available(),
                'title_formatted': transaction.offer.title_formatted(),
                'start_date': transaction.offer.start_date,
                'end_date': transaction.offer.end_date,
                'business': transaction.offer.business,
                'purchase_date': transaction.pub_date,
                'stock': transaction.unredeemed(),
                'redeemed': transaction.redemptions(),
                'image':{'image': transaction.offer.image},
                'description_100': transaction.offer.description_100()
            } for transaction in transactions
        ]

    except:
        pass

    return render(
        request,
        'offers_list_manage.html',
        template_parameters
    )


@login_required
def get_offers_by_status(
    request,
    status,
    business_id=None,
    city=None,
    neighborhood=None,
    category=None,
    premium=None,
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

        template_parameters['offers'] = Offer.objects.get_offers(
            status=status,
            business=business
        )

    except Exception, e:
        pass

    return render(
        request,
        'offers_list_manage.html',
        template_parameters
    )


def get_available_offers(
    request,
    business=None,
    city=None,
    neighborhood=None,
    category=None,
    premium=None,
    page='1',
    sort_by=OfferSort.NEWEST
):
    if request.method.lower() != 'get':
        return HttpResponseBadRequest(
            'GET is the only supported '
            'method for this request.'
        )

    template_parameters = {}

    try:
        business_instance = None
        if business:
            business_instance = Business.objects.get(
                backend_name=business.lower()
            )

        city_instance = None
        if city:
            city_instance = City.objects.get(name_denormalized=city.lower())

        neighborhood_instance = None
        if neighborhood:
            neighborhood_instance = Neighborhood.objects.get(
                name_denormalized=neighborhood.lower()
            )

        category_instance = None
        if category:
            category_instance = Category.objects.get(
                name_short=category.lower()
            )

        query = request.GET.get('query')

        template_parameters['offers'] = Offer.objects.get_available_offers(
            business_instance,
            city_instance,
            neighborhood_instance,
            category_instance,
            premium,
            int(page) if page else 1,
            query,
            sort_by.lower()
        )
    except Exception as e:
        pass

    return render(
        request,
        'offers_list.html',
        template_parameters
    )


def offer_map(
    request,
    business=None,
    city=None,
    neighborhood=None,
    category=None,
    premium=None,
    page='1',
    sort_by=OfferSort.NEWEST
):
    template_parameters = {}

    offers = None
    try:
        business_instance = None
        if business:
            business_instance = Business.objects.get(
                backend_name=business.lower()
            )

        city_instance = None
        if city:
            city_instance = City.objects.get(name_denormalized=city.lower())

        neighborhood_instance = None
        if neighborhood:
            neighborhood_instance = Neighborhood.objects.get(
                name_denormalized=neighborhood.lower()
            )

        category_instance = None
        if category:
            category_instance = Category.objects.get(
                name_short=category.lower()
            )

        query = request.GET.get('query')

        offers = \
            Offer.objects.get_available_offers(
                business_instance,
                city_instance,
                neighborhood_instance,
                category_instance,
                premium,
                int(page) if page else 1,
                query,
                sort_by
            )

    except:
        pass

    offer_map = OfferMap(
        settings.GOOGLE_MAPS_API_KEY,
        offers
    )
    template_parameters['map_script'] = offer_map.render()

    return render(
        request,
        'offer_map.html',
        template_parameters
    )


@login_required
def purchase(
    request,
    offer_id
):
    if request.method.lower() != 'post':
        return redirect('/offers/')

    template_parameters = ViewUtils.get_standard_template_parameters(request)

    try:
        offer = Offer.objects.get(pk=offer_id)
        template_parameters['offer'] = offer

        ipn_key = ''.join([
            request.user.id,
            '_',
            generate_ipn_hash(request.user.id)
        ])
        template_parameters['custom_data'] = ipn_key

        user = User.objects.get(pk=request.user.id)
        transaction = Transaction.objects.create_transaction(
            user,
            TransactionTypes.PENDING,
            offer.business,
            offer,
            None,
            offer.price_discount,
            ipn_key
        )

    except Exception, error:
        offer = None
        transaction = None

    if not offer:
        return HttpResponseNotFound('Could not find offer')

    if not transaction:
        return HttpResponseServerError('Failed to create transaction')

    template_parameters['paypal_button'] = render_paypal_button({
        'button_text': 'Buy your offers',
        'button_class': 'button radius-general',
        'paypal_parameters': {
            'cmd': '_cart',
            'upload': '1',
            'business': settings.PAYPAL_ACCOUNT,
            'shopping_url': settings.BASE_URL,
            'currency_code': 'USD',
            'return': '/'.join([
                settings.BASE_URL,
                'offers/dashboard/'
            ]),
            'notify_url': settings.PAYPAL_NOTIFY_URL,
            'rm': '2',
            'item_name_1': offer.title_formatted,
            'amount_1': offer.price_discount,
            'item_number_1': offer.id,
            'custom': transaction.transaction_context
        }
    })

    return render(
        request,
        'offer_purchase.html',
        template_parameters
    )

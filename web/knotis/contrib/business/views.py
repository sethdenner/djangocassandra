from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.forms import (
    Form,
    ModelForm,
    ModelChoiceField,
    CharField,
    URLField,
    ValidationError
)
from django.http import (
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponse
)
from django.shortcuts import (
    render,
    redirect
)
from django.template import Context
from django.template.loader import get_template
from django.utils.http import urlquote
from django.contrib.auth.decorators import login_required

from knotis.utils.view import (
    get_standard_template_parameters,
    format_currency
)
from knotis.contrib.business.models import (
    Business,
    BusinessLink,
    BusinessSubscription,
    clean_business_backend_name
)
from knotis.contrib.offer.models import (
    Offer,
    OfferStatus
)
from knotis.contrib.media.models import Image
from knotis.contrib.media.views import render_image_list
from knotis.contrib.auth.models import (
    KnotisUser
)
from knotis.contrib.qrcode.models import (
    Qrcode,
    QrcodeTypes
)
from knotis.contrib.yelp.views import get_reviews_by_yelp_id
from knotis.contrib.twitter.views import get_twitter_feed_html
from knotis.contrib.paypal.views import (
    render_paypal_button,
    generate_ipn_hash
)

from knotis.contrib.legacy.models import QrcodeIdMap


class CreateBusinessForm(Form):
    user = ModelChoiceField(label="User", queryset=KnotisUser.objects.all())
    backend_name = CharField(label="Backend Name", max_length=100)
    business_name = CharField(label="Business Name", max_length=100, required=False)
    avatar = URLField(label="Avatar URI.", required=False)
    hours = CharField(label="Business Hours", max_length=100, required=False)

    def clean_business_name(self):
        name = self.cleaned_data['name']
        if clean_business_backend_name(
            name
        ) in settings.BUSINESS_NAME_BLACKLIST:
            raise ValidationError('That business name is not allowed.')

        return name


class UpdateBusinessForm(Form):
    name = CharField(label='Name')
    summary = CharField(label='Summary', max_length=140, required=False)
    description = CharField(label='Description', required=False)
    address = CharField(label='Address', required=False)
    phone = CharField(label='Phone', required=False)
    twitter_name = CharField(label='Twitter', required=False)
    facebook_uri = CharField(label='Facebook', required=False)
    yelp_id = CharField(label='Yelp ID', required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        if clean_business_backend_name(
            name
        ) in settings.BUSINESS_NAME_BLACKLIST:
            raise ValidationError('That business name is not allowed.')

        return name


class AddBusinessLinkForm(ModelForm):
    class Meta:
        model = BusinessLink
        exclude = ('business')


@login_required
def delete_link(
        request,
        link_id
):
    if request.method.lower() != 'post':
        return HttpResponseBadRequest('Method must be post.')

    try:
        link = BusinessLink.objects.get(id=link_id)

    except:
        link = None

    if not link:
        return HttpResponseNotFound('Could not find business link.')

    if link.business.user_id != request.user.id:
        return HttpResponseBadRequest('Business link does not belong to user.')

    try:
        link.delete()
        return HttpResponse('OK')

    except:
        logger.exception('failed to delete business link.')
        return HttpResponseServerError('failed to delete business link')


@login_required
def set_primary_image(
    request,
    business_id,
    image_id
):
    if request.method.lower() != 'post':
        return HttpResponseBadRequest('Method must be post.')

    try:
        business = Business.objects.get(pk=business_id)

    except:
        business = None

    if not business:
        return HttpResponseNotFound('Business not found.')

    if business.user_id != request.user.id:
        return HttpResponseBadRequest('Business does not belong to logged in user!')

    try:
        image = Image.objects.get(pk=image_id)

    except:
        image = None

    if not image:
        return HttpResponseNotFound('Image not found')

    if business.id != image.related_object_id:
        return HttpResponseBadRequest('Image does not belong to business!')

    business.primary_image = image
    try:
        business.save()

    except:
        return HttpResponseServerError('Could not save primary image')

    return HttpResponse('OK')


@login_required
def edit_profile(request):
    update_form = None
    link_form = None

    business = None
    try:
        user = KnotisUser.objects.get(pk=request.user.id)
        business = Business.objects.get(user=user)

    except Business.DoesNotExist:
        business = None

    except:
        user = None
        business = None

    if request.method.lower() == 'post':
        if 'submit_profile' in request.POST:
            update_form = UpdateBusinessForm(request.POST)
            if update_form.is_valid():
                if business:
                    business.update(
                        **update_form.cleaned_data
                    )

                else:
                    business = Business.objects.create_business(
                        user,
                        **update_form.cleaned_data
                    )
                    # Create QR Code for business.
                    Qrcode.objects.create(
                        business=business,
                        uri=settings.BASE_URL + '/' + business.backend_name + '/',
                        qrcode_type=QrcodeTypes.PROFILE
                    )

        elif 'submit_links' in request.POST:
            link_form = AddBusinessLinkForm(request.POST)
            if link_form.is_valid():
                BusinessLink.objects.create(
                    business=business,
                    **link_form.cleaned_data
                )

    template_parameters = get_standard_template_parameters(request)

    if not update_form:
        if business:
            business_values = {
                'name': business.business_name.value if business.business_name else None,
                'summary': business.summary.value if business.summary else None,
                'description': business.description.value if business.description else None,
                'address': business.address.value.value if business.address else None,
                'phone': business.phone.value.value if business.phone else None,
                'twitter_name': business.twitter_name.value.value if business.twitter_name else None,
                'facebook_uri': business.facebook_uri.value.value if business.facebook_uri else None,
                'yelp_id': business.yelp_id.value.value if business.yelp_id else None
            }
            update_form = UpdateBusinessForm(business_values)

        else:
            update_form = UpdateBusinessForm()

    try:
        template_parameters['business_links'] = BusinessLink.objects.filter(business=business)

    except:
        pass

    template_parameters['business'] = business
    template_parameters['update_form'] = update_form
    template_parameters['link_form'] = link_form if link_form else AddBusinessLinkForm()
    template_parameters['do_upload'] = True
    template_parameters['gallery'] = True
    template_parameters['scripts'] = [
        'views/business.profile.js'
    ]

    try:
        images = Image.objects.filter(related_object_id=business.id)
        options = {
            'alt_text': business.business_name.value,
            'images': images,
            'business': business,
            'dimensions': '35x19',
            'image_class': 'business-gallery'
        }
        template_parameters['image_list'] = render_image_list(options)
    except:
        logger.exception('rending image list failed')

    return render(
        request,
        'edit_business_profile.html',
        template_parameters
    )


@login_required
def services(request):
    template_parameters = get_standard_template_parameters(request)

    template_parameters['subscription_price'] = format_currency(
        settings.PRICE_MERCHANT_MONTHLY
    )

    template_parameters['paypal_button'] = render_paypal_button({
        'button_text': 'Buy Subscription',
        'button_class': 'button radius-general',
        'paypal_parameters': {
            'cmd': '_s-xclick',
            'hosted_button_id': settings.PAYPAL_PREMIUM_BUTTON_ID,
            'notify_url': '/'.join([
                settings.BASE_URL,
                'paypal',
                'ipn',
                ''
            ]),
            'item_name_1': 'Business Monthly Subscription',
            'custom': '|'.join([
                request.user.id,
                generate_ipn_hash(request.user.id)
            ]),
        }
    })

    return render(
        request,
        'manage_services.html',
        template_parameters
    )


def profile(request, backend_name):
    template_parameters = get_standard_template_parameters(request)

    business = None
    try:
        business = Business.objects.get(backend_name=urlquote(backend_name))
    except:
        pass

    if not business:
        return redirect('/')

    template_parameters['business'] = business

    if business.yelp_id and business.yelp_id.value.value:
        try:
            template_parameters['yelp_reviews'] = get_reviews_by_yelp_id(business.yelp_id.value.value)
        
        except:
            logger.exception('exception while getting yelp reviews')

    if business.twitter_name and business.twitter_name.value.value:
        template_parameters['twitter_feed'] = get_twitter_feed_html(
            business.twitter_name.value.value,
            2
        )

    try:
        template_parameters['business_links'] = BusinessLink.objects.filter(business=business)
        subscriptions = BusinessSubscription.objects.filter(
            business=business,
            active=True
        )
        template_parameters['subscriptions'] = subscriptions
        template_parameters['subscribed_users'] = BusinessSubscription.objects.get_users_subscribed_to_business(
            business,
            subscriptions
        )
    except:
        pass

    try:
        business_images = Image.objects.filter(related_object_id=business.id)
        template_parameters['business_images'] = business_images;
        if not business.primary_image and len(business_images):
            business.primary_image = business_images[0]
            business.save()

    except:
        pass

    try:
        qrcode = Qrcode.objects.filter(business=business)[0]

        try:
            id_map = QrcodeIdMap.objects.get(new_qrcode=qrcode)

        except Exception, e:
            id_map = None

        if id_map:
            qrcode_uri = '/'.join([
                settings.BASE_URL,
                'business',
                unicode(id_map.old_id),
            ])

        else:
            qrcode_uri = '/'.join([
                settings.BASE_URL,
                'qrcode',
                qrcode.id
            ])

        template_parameters['qrcode_uri'] = qrcode_uri

    except Exception, e:
        pass

    try:
        template_parameters['current_offers'] = Offer.objects.filter(
            business=business,
            status=OfferStatus.CURRENT
        )
    except:
        pass

    template_parameters['gallery'] = True

    return render(
        request,
        'business_profile.html',
        template_parameters
    )


@login_required
def follow(
    request,
    subscribe
):
    if request.method.lower() != 'post':
        return HttpResponseBadRequest()

    business_id = request.POST.get('business_id')
    if not business_id:
        return HttpResponseNotFound()

    business = None
    try:
        business = Business.objects.get(pk=business_id)
    except:
        pass

    knotis_user = None
    try:
        knotis_user = KnotisUser.objects.get(pk=request.user.id)
    except:
        pass

    if not business or not knotis_user:
        return HttpResponseNotFound()

    existing = None
    try:
        existing = BusinessSubscription.objects.filter(
            user=knotis_user,
            business=business
        )[0]
    except:
        pass

    if existing:
        try:
            existing.active = subscribe
            existing.save()
        except:
            return HttpResponseBadRequest()
    else:
        try:
            BusinessSubscription.objects.create(
                user=knotis_user,
                business=business
            )
        except:
            return HttpResponseBadRequest()

    template_parameters = {
        'knotis_user': knotis_user
    }

    return render(
        request,
        'business_profile_follower.html',
        template_parameters
    )


def subscriptions(request):
    template_parameters = get_standard_template_parameters(request)

    subscriptions = None
    try:
        subscriptions = BusinessSubscription.objects.filter(
            user=request.user,
            active=True
        )
    except:
        pass

    template_parameters['subscriptions'] = subscriptions

    try:
        template_parameters['offers'] = (
            Offer.objects.get_subscribed_businesses_offers_dict(subscriptions)
        )
    except:
        pass

    return render(
        request,
        'subscriptions.html',
        template_parameters
    )
    
    
def get_business_rows(
    request,
    page='1',
    count='12',
):
    page = int(page)
    count = int(count)
    
    page = page - 1
    if page < 0:
        page = 0
        
    bpr = 3
    options = {
        'init': page*count,
        'rows': count/bpr,
        'bpr': bpr
    }
    
    query = request.GET.get('query')
    
    return render_business_rows(
        options,
        request,
        query
    )
    
    
def render_business_rows(
    options=None, 
    request=None,
    query=None
):
    default_options = {
        'init': 0,
        'rows': 4,
        'bpr': 3
    }
    if options:
        default_options.update(options)
        
    options = default_options

    init = options['init']
    rows = options['rows']
    bpr = options['bpr']
    
    priority_businesses = []
    total_priority_businesses = 0
    
    for name in settings.PRIORITY_BUSINESS_NAMES:
        try:
            business = Business.objects.get(backend_name=name)
            valid = True
            if query:
                valid = business.search(query)
            
            if valid:
                priority_businesses.append(business)
                total_priority_businesses = total_priority_businesses + 1

        except:
            continue
                
    priority_businesses = priority_businesses[init:init + rows*bpr]
            
    if len(priority_businesses):
        init = 0
    
    else:
        init = init - total_priority_businesses
        
    logger.debug('init: %s' % init, )
                
    vacant_slots = rows*bpr - len(priority_businesses)
    businesses = []
    if vacant_slots:
        try:
            if query:
                all_businesses = Business.objects.all()
                business_results = []
                for business in all_businesses:
                    if business.search(query):
                        business_results.append(business)
                        
                
                businesses += business_results[init:init + vacant_slots]
            
            else:
                businesses += Business.objects.all()[init:init + vacant_slots]
        
        except:
            pass
        
    businesses = priority_businesses + businesses
    if not businesses:
        if request:
            return HttpResponse('')
        
        else:
            return ''
        
    business_rows = [[
            business for business in businesses[x*bpr:x*bpr + bpr]
        ] for x in range(0, rows)
    ]

    options['business_rows'] = business_rows 
    options['render_about'] = None == request
    options['STATIC_URL'] = settings.STATIC_URL

    if request:
        return render(
            request,
            'business_row.html',
            options
        )

    else:
        context = Context(options)
        business_row = get_template('business_row.html')
        return business_row.render(context)
import urllib

from app.models.businesses import Business, BusinessLink, \
    BusinessSubscription, clean_business_name
from app.models.offers import Offer, OfferStatus
from app.models.media import Image
from app.utils import View as ViewUtils
from django.conf import settings
from django.forms import Form, ModelForm, ModelChoiceField, CharField, \
    URLField, ValidationError
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.http import urlquote
from django.contrib.auth.decorators import login_required

from knotis_auth.models import User, UserProfile, AccountTypes
from knotis_qrcodes.models import Qrcode, QrcodeTypes
from knotis_yelp.views import get_reviews_by_yelp_id
from knotis_twitter.views import get_twitter_feed_html

from legacy.models import QrcodeIdMap


class CreateBusinessForm(Form):
    user = ModelChoiceField(label="User", queryset=User.objects.all())
    backend_name = CharField(label="Backend Name", max_length=100)
    business_name = CharField(label="Business Name", max_length=100, required=False)
    avatar = URLField(label="Avatar URI.", required=False)
    hours = CharField(label="Business Hours", max_length=100, required=False)


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
        if clean_business_name(
            name
        ) in settings.BUSINESS_NAME_BLACKLIST:
            raise ValidationError('That business name is not allowed.')

        return name


class AddBusinessLinkForm(ModelForm):
    class Meta:
        model = BusinessLink
        exclude = ('business')


@login_required
def edit_profile(request):
    update_form = None
    link_form = None

    business = None
    try:
        business = Business.objects.get(user=request.user)

    except Business.DoesNotExist:
        pass #fine

    except:
        pass #fatal

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
                        request.user,
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

    template_parameters = ViewUtils.get_standard_template_parameters(request)

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
    
    try:
        template_parameters['images'] = Image.objects.filter(related_object_id=business.id)
    except:
        pass

    return render(
        request,
        'edit_business_profile.html',
        template_parameters
    )


@login_required
def services(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    template_parameters['user_profile'] = UserProfile.objects.get(user=request.user)
    template_parameters['AccountTypes'] = AccountTypes
    template_parameters['subscription_price'] = ("%.2f" % round(
            settings.PRICE_MERCHANT_MONTHLY,
            2
        )).replace('.00', '')

    return render(
        request,
        'manage_services.html',
        template_parameters
    )


def profile(request, backend_name):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    business = None
    try:
        business = Business.objects.get(backend_name=urlquote(backend_name))
    except:
        pass

    if not business:
        return redirect('/')

    template_parameters['business'] = business
    
    if business.yelp_id and business.yelp_id.value.value:
        template_parameters['yelp_reviews'] = get_reviews_by_yelp_id(business.yelp_id.value.value)
        
    if business.twitter_name and business.twitter_name.value.value:
        template_parameters['twitter_feed'] =  get_twitter_feed_html(
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
        knotis_user = User.objects.get(pk=request.user.id)
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
    template_parameters = ViewUtils.get_standard_template_parameters(request)

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
        template_parameters['offers'] = Offer.objects.get_subscribed_businesses_offers_dict(subscriptions)
    except:
        pass

    return render(
        request,
        'subscriptions.html',
        template_parameters
    )

from django.shortcuts import redirect

from knotis.apps.legacy.models import (
    BusinessIdMap,
    OfferIdMap
)
from knotis.apps.qrcode.models import Qrcode
from knotis.apps.paypal.views import ipn_callback

LEGACY_URL_MAP = {
    '/deals/': '/offers/',
    '/category/contact/': '/contact/',
    '/home/account/': '/plans/',
    '/home/login/': '/login/',
    '/backend/user/': '/profile/',
    '/backend/': '/offers/dashboard/',
    '/category/page/12/': '/about/',
    '/category/page/14/': '/howitworks/',
    '/category/page/27/': '/story/',
    '/category/page/22/': '/inquire/',
    '/category/page/26/': '/support/',
    '/category/terms_of_use/': '/terms/',
    '/category/privacy_policy/': '/privacy/',
}


def map_redirect(request):
    return redirect(
        LEGACY_URL_MAP[request.path],
        permanent=True
    )


def map_paypal_ipn(request):
    return ipn_callback(request)


def offer_city_filter_redirect(
    request,
    city_name,
    neighborhood_name=None
):
    return redirect(
        ''.join([
            '/offers/?city=%s' % (city_name,),
            '&neighborhood=%s' % (neighborhood_name,) if neighborhood_name else ''
        ])
    )


def business_profile_redirect(
    request,
    legacy_business_id
):
    business = None
    try:
        id_map = BusinessIdMap.objects.get(old_id=legacy_business_id)
        business = id_map.business

    except:
        pass

    if None == business:
        # can't redirect properly. drop on main page.
        return redirect('/')

    return redirect(
        '/%s/' % (business.backend_name,),
        premanent=True
    )


def offer_profile_redirect(
    request,
    legacy_offer_id
):
    offer = None
    try:
        id_map = OfferIdMap.objects.get(old_id=legacy_offer_id)
        offer = id_map.new_offer

    except:
        pass

    if None == offer:
        # can't redirect properly. drop on main page.
        return redirect('/')

    return redirect(
        '/offer/%s/' % (offer.id,),
        premanent=True
    )


def qrcode_redirect(
    request,
    legacy_business_id
):
    qrcode = None
    try:
        id_map = BusinessIdMap.objects.get(old_id=legacy_business_id)
        qrcode = Qrcode.objects.filter(business=id_map.business)[0]
    except:
        pass

    if None == qrcode:
        # can't redirect properly. drop on main page.
        return redirect('/')

    return redirect(
        'qrcode/%s/' % (qrcode.id),
        premanent=True
    )

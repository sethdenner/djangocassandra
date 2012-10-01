from django.shortcuts import render
from django.conf import settings

from app.models.contents import Content
from app.models.offers import Offer
from app.utils import View as ViewUtils

from knotis_maps.views import OfferMap


def index(
    request,
    login
):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    content = {}

    content_set = Content.objects.get_template_content('home')
    for c in content_set:
        content[c.name] = c.value

    template_parameters.update(content)

    if 'login' == login:
        template_parameters['login'] = True

    try:
        premium_offers = Offer.objects.get_available_offers(premium=True)[:4]
        template_parameters['premium_offers'] = premium_offers
    except:
        premium_offers = None
        template_parameters['premium_offers'] = premium_offers

    offer_map = OfferMap(
        settings.GOOGLE_MAPS_API_KEY,
        premium_offers
    )
    template_parameters['google_map_api_script'] = offer_map.render_api_js()
    template_parameters['map_script'] = offer_map.render() 

    return render(
        request,
        'home.html',
        template_parameters
    )


def plans(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    content = {}

    content_set = Content.objects.get_template_content('plans')
    for c in content_set:
        content[c.name] = c.value

    template_parameters.update(content)

    return render(
        request,
        'plans.html',
        template_parameters
    )


def about(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'about.html',
        template_parameters
    )


def how_it_works(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'how_it_works.html',
        template_parameters
    )


def story(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'story.html',
        template_parameters
    )


def inquire(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'inquire.html',
        template_parameters
    )


def support(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'support.html',
        template_parameters
    )


def terms(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'terms.html',
        template_parameters
    )


def privacy(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'privacy.html',
        template_parameters
    )

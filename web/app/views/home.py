from django.shortcuts import render
from django.conf import settings

from app.models.contents import Content
from app.models.offers import Offer, OfferTypes
from app.utils import View as ViewUtils

from pymaps.pymaps import Icon, PyMap

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
        template_parameters['premium_offers'] = Offer.objects.filter(offer_type=OfferTypes.PREMIUM)
    except:
        pass

    '''
    icon = Icon()
    gmap.addicon(icon)
    point0 = [1, 1]
    point1 = [2, 4, 'hello']
    point3 = [21, 4, None, icon]
    gmap.maps[0].setpoint(point0)
    gmap.maps[0].setpoint(point1)
    gmap.maps[0].setpoint(point3)
    template_parameters['map'] = gmap.pymapjs()
    '''
    gmap = PyMap()
    gmap.key = settings.GOOGLE_MAPS_API_KEY
    template_parameters['map_script'] = gmap.headerjs()

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


def contact(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    template_parameters['current_page'] = 'contact'

    return render(
        request,
        'contact.html',
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

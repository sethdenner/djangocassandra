import logging

from django.shortcuts import render
from django.conf import settings

from knotis.utils.view import get_standard_template_parameters
from knotis.apps.content.models import Content
from knotis.apps.business.models import Business

logger = logging.getLogger(__name__)

def index(
    request,
    login
):
    logger.info(
        'Request', { 
            'request': request 
        }
    )
    template_parameters = get_standard_template_parameters(request)

    content = {}

    content_set = Content.objects.get_template_content('home')
    for c in content_set:
        content[c.name] = c.value

    template_parameters.update(content)

    if 'login' == login:
        template_parameters['login'] = True

    try:
        init = 0
        rows = 4
        bpr = 3
        
        businesses = []
        for backend_name in settings.PRIORITY_BUSINESS_NAMES[init:init + rows*bpr]:
            try:
                businesses.append(Business.objects.get(backend_name=backend_name))
                
            except:
                continue
            
        business_rows = [[
                business for business in businesses[x*bpr:x*bpr + bpr]
            ] for x in range(0, rows)
        ]
        
        template_parameters['business_rows'] = business_rows

    except:
        businesses = None

    return render(
        request,
        'home.html',
        template_parameters
    )


def plans(request):
    template_parameters = get_standard_template_parameters(request)

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
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'about.html',
        template_parameters
    )


def how_it_works(request):
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'how_it_works.html',
        template_parameters
    )


def story(request):
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'story.html',
        template_parameters
    )


def inquire(request):
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'inquire.html',
        template_parameters
    )


def support(request):
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'support.html',
        template_parameters
    )


def terms(request):
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'terms.html',
        template_parameters
    )


def privacy(request):
    template_parameters = get_standard_template_parameters(request)

    return render(
        request,
        'privacy.html',
        template_parameters
    )

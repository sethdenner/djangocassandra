from django.shortcuts import render
from django.template.context import RequestContext
from app.models.contents import Content
from app.utils import User as UserUtils, View as ViewUtils
from app.models.users import UserProfile

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

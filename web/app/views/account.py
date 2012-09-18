from django.shortcuts import render

from app.utils import View as ViewUtils
from app.models.contents import Content


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

from django.shortcuts import render

from app.utils import View as ViewUtils

def events(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    template_parameters['current_page'] = 'events'

    return render(
        request,
        'events.html',
        template_parameters
    )

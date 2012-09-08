from django.shortcuts import render

from app.utils import View as ViewUtils

def happy_hours(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    template_parameters['current_page'] = 'happy_hours'

    return render(
        request,
        'happy_hours.html',
        template_parameters
    )

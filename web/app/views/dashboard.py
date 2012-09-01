from django.shortcuts import render

from app.utils import View as ViewUtils

def dashboard(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    
    return render(
        request,
        'dashboard.html',
        template_parameters
    )
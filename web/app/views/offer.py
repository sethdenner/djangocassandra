from django.shortcuts import render

from app.utils import View as ViewUtils


def offers(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    
    return render(
        request,
        'offers.html',
        template_parameters
    )
    

def create(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)
    
    return render(
        request,
        'create_offer.html',
        template_parameters
    )
    
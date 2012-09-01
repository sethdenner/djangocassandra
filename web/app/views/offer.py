from django.shortcuts import render

def offers(request):
    return render(
        request,
        'offers.html',
        {}
    )
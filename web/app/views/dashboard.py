from django.shortcuts import render

def dashboard(request):
    render(
        request,
        'dashboard.html',
        {}
    )
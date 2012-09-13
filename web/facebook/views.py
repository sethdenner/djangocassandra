from django.shortcuts import render


def channel(request):
    return render(
        request,
        'channel.html',
        {}
    )

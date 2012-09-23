from django.shortcuts import render


def channel(request):
    return render(
        request,
        'channel.html',
        {}
    )


def get_facebook_avatar(facebook_id):
    if not facebook_id:
        return None
    
    return '/'.join([
        'http://graph.facebook.com',
        facebook_id,
        'picture'
    ])

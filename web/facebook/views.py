import json
import hashlib

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login

from app.models.endpoints import EndpointEmail
from knotis_auth.models import User, AccountStatus, AccountTypes


FACEBOOK_PASSWORD_SALT = '@#^#$@FBb9xc8cy'


def channel(request):
    return render(
        request,
        'channel.html',
        {}
    )


def login(
    request,
    account_type=AccountTypes.USER
):
    def generate_response(data):
        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )

    if request.method.lower() != 'post':
        return HttpResponseBadRequest('Only POST is supported.')

    try:
        auth_response = request.POST['data']['response']['authResponse']
        facebook_user = request.POST['data']['user']
    except:
        return HttpResponseBadRequest('No data returned from facebook')
        pass

    user = None
    try:
        user = User.objects.get(username=facebook_user['email'])
    except:
        pass

    if None == user:
        try:
            password = ''.join([
                FACEBOOK_PASSWORD_SALT,
                auth_response['userID'],
                FACEBOOK_PASSWORD_SALT
            ])
            password_hash = hashlib.md5(password)

            user, user_profile = User(
                first_name=facebook_user['first_name'],
                last_name=facebook_user['last_name'],
                email=facebook_user['email'],
                password=password_hash.hexdigest()
            )
            user.active = True
            user.save()

            user_profile.status = AccountStatus.ACTIVE
            user_profile.account_type = account_type
            user_profile.save()

            EndpointEmail.objects.create_endpoint(
                user,
                user.username,
                primary=True
            )
        except:
            pass

    if None == user:
        return generate_response({
            'success': 'no',
            'message': 'Failed to associate your Facebook account with your Knotis account. Please try again.'
        })

    authenticated_user = authenticate(
        username=user.username,
        password=''.join([
            FACEBOOK_PASSWORD_SALT,
            auth_response['userID'],
            FACEBOOK_PASSWORD_SALT
        ])
    )

    if authenticated_user:
        django_login(
            request,
            user
        )
        return generate_response({
            'success': 'yes',
            'user': account_type
        })
    else:
        return generate_response({
            'success': 'no',
            'message': 'Failed authenticate Facebook user.'
        })

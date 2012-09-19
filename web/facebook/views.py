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
        facebook_id = request.POST['data[response][authResponse][userID]']
        email = request.POST['data[user][email]']
        first_name = request.POST['data[user][last_name]']
        last_name = request.POST['data[user][last_name]']

    except:
        return HttpResponseBadRequest('No data returned from facebook')
        pass

    user = None
    try:
        user = User.objects.get(username=email)
    except:
        pass

    message = None
    if None == user:
        try:
            password = ''.join([
                FACEBOOK_PASSWORD_SALT,
                facebook_id,
                FACEBOOK_PASSWORD_SALT
            ])
            password_hash = hashlib.md5(password)

            user, user_profile = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
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
        except Exception as e:
            message = str(e)

    if None == user:
        return generate_response({
            'success': 'no',
            'message': (
                'Failed to associate your Facebook account '
                'with your Knotis account. Please try again. %s'
            ) % message,
        })

    password = ''.join([
        FACEBOOK_PASSWORD_SALT,
        facebook_id,
        FACEBOOK_PASSWORD_SALT
    ])
    password_hash = hashlib.md5(password)
    authenticated_user = authenticate(
        username=user.username,
        password=password_hash.hexdigest()
    )

    if authenticated_user:
        django_login(
            request,
            authenticated_user
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

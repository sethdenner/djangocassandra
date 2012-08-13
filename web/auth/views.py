from django.shortcuts import render_to_response

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm


class KnotisAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(KnotisAuthenticationForm, self).__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs = {
            'class': 'radius-general',
            'id': 'email',
            'type': 'text',
            'name': 'username',
            'placeholder': 'Username',
            'autofocus': None
        }
        
        self.fields['password'].widget.attrs = {
            'class': 'radius-general',
            'id': 'password',
            'type': 'password',
            'name': 'password',
            'placeholder': 'Password',
        }


def login_user(request):
    def generate_response(username):
        return render_to_response('login.html', {'username': username})

    username = ''

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            # Message user about failed login attempt.
            return generate_response(username)

        if not user.is_active():
            # Message user about account deactivation.
            return generate_response(username)

        login(request, user)

    return generate_response(username)

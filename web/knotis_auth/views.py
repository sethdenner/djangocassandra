import json

from django.forms import CharField, EmailField, BooleanField, PasswordInput, \
    HiddenInput, CheckboxInput, Form, ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, \
    logout as django_logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.http import HttpResponse

from knotis_auth.models import User

from app.utils import View as ViewUtils


class SignUpForm(Form):
    first_name = CharField(label='First Name')
    last_name = CharField(label='Last Name')
    email = EmailField(label='Email Address')
    password = CharField(widget=PasswordInput, label='Password')
    account_type = CharField(widget=HiddenInput)
    business = BooleanField(widget=CheckboxInput, required=False)

    def __init__(self, *args, **kwargs):
        account_type = kwargs.pop('account_type') \
            if 'account_type' in kwargs else 0

        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'First Name',
            'autofocus': None,
        }

        self.fields['last_name'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'Last Name',
        }

        self.fields['email'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'Email',
        }

        self.fields['password'].widget.attrs = {
            'class': 'radius-general',
            'placeholder': 'Password',
        }

        self.fields['account_type'].widget.attrs = {
            'value': account_type
        }

        self.fields['business'].widget.attrs = {
            'checked': None,
            'value': '1'
        }

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email):
            raise ValidationError(_("This email address is already in use. Please supply a different email address."))
        return email


def sign_up(request, account_type='user'):
    if account_type == 'foreverfree':
        account_type_int = 1
    elif account_type == 'premium':
        account_type_int = 2
    else:
        account_type_int = 0

    form = SignUpForm(account_type=account_type_int)
    return render(
        request,
        'sign_up.html', {
        'form': form,
        'account_type': account_type,
    })


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


class KnotisPasswordChangeForm(Form):
    old_password = CharField(label='Old Pass', widget=PasswordInput)
    new_password = CharField(label='New Pass', widget=PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super(KnotisPasswordChangeForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError('Your old password was entered incorrectly. Please enter it again.')
        return old_password


def login(request):
    def generate_response(data):
        if request.method == 'POST':
            return HttpResponse(
                json.dumps(data),
                content_type='application/json'
            )
        elif request.method == 'GET':
            form = KnotisAuthenticationForm()
            return render(
                request,
                'login.html', {
                    'form': form
                }
            )

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            username=username,
            password=password
        )

        if not user:
            # Message user about failed login attempt.
            return generate_response({
                'success': 'no',
                'message': 'Login failed. Please try again.'
            })

        if not user.is_active:
            # Message user about account deactivation.
            return generate_response({
                'success': 'no',
                'message': 'This account is inactive. Please contact support.'
            })

        django_login(
            request,
            user
        )

        return generate_response({
            'success': 'yes',
            'redirect': 1
        })

    else:
        return generate_response(None)


def logout(request):
    django_logout(request)
    return redirect('/')


def validate(
    request,
    user_id,
    validation_key
):
    redirect_url = '/'
    if (User.activate_user(
        user_id,
        validation_key
    )):
        redirect_url = settings.LOGIN_URL

    return redirect(
        redirect_url
    )


def password_forgot(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'password_forgot.html',
        template_parameters
    )


def password_reset(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    return render(
        request,
        'password_reset.html',
        template_parameters
    )

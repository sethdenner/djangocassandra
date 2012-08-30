from django.forms import CharField, EmailField, BooleanField, PasswordInput, \
    HiddenInput, CheckboxInput, Form, ValidationError
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from knotis_auth.models import User


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


def login_user(request):
    def generate_response(username):
        return render(request, 'login.html', {'username': username})

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

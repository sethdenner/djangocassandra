import hashlib
import json
import uuid

from django.forms import CharField, EmailField, BooleanField, PasswordInput, \
    HiddenInput, CheckboxInput, Form, ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, \
    logout as django_logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.html import strip_tags
from django.template import Context
from django.template.loader import get_template
from django.core.urlresolvers import reverse

from paypal.views import render_paypal_button, generate_ipn_hash

from knotis_auth.models import User, UserProfile, AccountStatus, AccountTypes

from app.utils import View as ViewUtils, Email as EmailUtils
from app.models.endpoints import Endpoint, EndpointTypes




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
            raise ValidationError("This email address is already in use. Please supply a different email address.")
        return email

    def create_user(
        self,
        request
    ):
        return User.objects.create_user(
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name'],
            self.cleaned_data['email'],
            self.cleaned_data['password'],
            self.cleaned_data['account_type'],
            self.cleaned_data['business']
        )


def sign_up(request, account_type=AccountTypes.USER):
    if request.method == 'POST':
        response_data = {
            'success': 'no',
        }
        feedback = ''
        error = ''

        sign_up_form = SignUpForm(request.POST)
        user = None
        user_profile = None
        if sign_up_form.is_valid():
            try:
                user, user_profile = sign_up_form.create_user(request)

                email = Endpoint.objects.create_endpoint(
                    EndpointTypes.EMAIL,
                    user.username,
                    user,
                    True
                )

                #TODO This should be handled by an async task
                if user_profile.account_type == AccountTypes.BUSINESS_FREE:
                    subject = 'New Free Business Account in Knotis'

                elif user_profile.account_type == AccountTypes.BUSINESS_MONTHLY:
                    subject = 'New Premium Business Account in Knotis'

                else:
                    subject = 'New user Account in Knotis'

                try:
                    EmailUtils.generate_email(
                        'activate',
                        subject,
                        settings.EMAIL_HOST_USER,
                        [email.value.value], {
                            'user_id': user.id,
                            'validation_key': email.validation_key,
                            'BASE_URL': settings.BASE_URL,
                            'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
                            'SERVICE_NAME': settings.SERVICE_NAME
                        }
                    ).send()

                except:
                    pass

                response_data['success'] = 'yes'
                response_data['user'] = user_profile.account_type

                if True == sign_up_form.cleaned_data['business']:
                    if user_profile.account_type == AccountTypes.BUSINESS_FREE:
                        feedback = 'Your Forever Free account has been created'

                else:
                    feedback = 'Your free Knotis account has been created.'

            except Exception as e:
                error = 'There was an error creating your account: ' + e.message

        else:
            error = 'The following fields are invalid: '
            for e in sign_up_form.errors:
                error += strip_tags(e) + '<br/>'

        if error:
            response_data['message'] = error
            return HttpResponse(
                json.dumps(response_data),
                mimetype='application/json'
            )

        paypal_button = None
        if AccountTypes.BUSINESS_MONTHLY == user_profile.account_type:
            paypal_button = render_paypal_button({
                'hosted_button_id': settings.PAYPAL_PREMIUM_BUTTON_ID,
                'notify_url': reverse('paypal.views.buy_premium_service'),
                'item_1': 'subscription',
                'custom': '_'.join([
                    user.id,
                    generate_ipn_hash(user.id)
                ]),
            })

        html = get_template('finish_registration.html')
        context = Context({
            'AccountTypes': AccountTypes,
            'account_type': user_profile.account_type,
            'paypal_button': paypal_button,
            'feedback': feedback,
            'error': error
        })
        response_data['html'] = html.render(context)

        return HttpResponse(
            json.dumps(response_data),
            mimetype='application/json'
        )

    else:
        form = SignUpForm(account_type=account_type)
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

        if username:
            username = username.lower()

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

        user_profile = None
        try:
            user_profile = UserProfile.objects.get(user=user)
        except:
            pass

        if not user_profile or user_profile.account_status != AccountStatus.ACTIVE:
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


FACEBOOK_PASSWORD_SALT = '@#^#$@FBb9xc8cy'


def _generate_facebook_password(facebook_id):
    password = ''.join([
        FACEBOOK_PASSWORD_SALT,
        facebook_id,
        FACEBOOK_PASSWORD_SALT
    ])
    password_hash = hashlib.md5(password)
    return password_hash.hexdigest()


def _authenticate_facebook(
    username,
    facebook_id
):
    password = ''.join([
        FACEBOOK_PASSWORD_SALT,
        facebook_id,
        FACEBOOK_PASSWORD_SALT
    ])
    password_hash = hashlib.md5(password)
    return authenticate(
        username=username,
        password=password_hash.hexdigest()
    )


def facebook_login(
    request,
    account_type=None
):
    def generate_response(data):
        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )

    if request.method.lower() != 'post':
        return HttpResponseBadRequest('Only POST is supported.')

    try:
        facebook_id = request.POST.get('data[response][authResponse][userID]')
        email = request.POST.get('data[user][email]')
        first_name = request.POST.get('data[user][first_name]')
        last_name = request.POST.get('data[user][last_name]')

    except:
        return HttpResponseBadRequest('No data returned from facebook')
        pass

    if request.session.get('fb_id') == facebook_id:
        django_login(
            request,
            _authenticate_facebook(
                email,
                facebook_id
            )
        )

        return generate_response({
            'success': 'no',
            'message': 'Already authenticated.'
        })

    user = None
    try:
        user = User.objects.get(username=email)
    except:
        pass

    message = None
    user_profile = None
    if None == user and account_type:
        try:
            user, user_profile = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=_generate_facebook_password(facebook_id)
            )
            user.active = True
            user.save()

            user_profile.status = AccountStatus.ACTIVE
            user_profile.account_type = account_type
            user_profile.save()

            Endpoint.objects.create_endpoint(
                EndpointTypes.EMAIL,
                user.username,
                user,
                True
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

    if None == user_profile:
        user_profile = UserProfile.objects.get(user=user)

    authenticated_user = _authenticate_facebook(
        user.username,
        facebook_id
    )

    if authenticated_user:
        django_login(
            request,
            authenticated_user
        )

        request.session['fb_id'] = facebook_id

        if account_type:
            data = {
                'success': 'yes',
                'user': account_type
            }

            if AccountTypes.BUSINESS_MONTHLY == account_type:
                paypal_button = None
                if AccountTypes.BUSINESS_MONTHLY == user_profile.account_type:
                    paypal_button = render_paypal_button({
                        'hosted_button_id': settings.PAYPAL_PREMIUM_BUTTON_ID,
                        'notify_url': reverse('paypal.views.buy_premium_service'),
                        'item_1': 'subscription',
                        'custom': '_'.join([
                            user.id,
                            generate_ipn_hash(user.id)
                        ])
                    })

                html = get_template('finish_registration.html')
                context = Context({
                    'AccountTypes': AccountTypes,
                    'account_type': user_profile.account_type,
                    'paypal_button': paypal_button,
                })
                data['message'] = html.render(context)


            return generate_response(data)

        else:
            return generate_response({
                'success': 'yes',
                'message': 'Authentication successful.'
            })
    elif user:
        return generate_response({
            'success': 'no',
            'message': 'You already have an account on Knotis. Please login with your Knotis credentials.'
        })
    else:
        return generate_response({
            'success': 'no',
            'message': 'Failed to authenticate facebook user.'
        })


def logout(request):
    django_logout(request)
    return redirect('/')


def validate(
    request,
    user_id,
    validation_key
):
    redirect_url = '/'

    try:
        user = User.objects.get(pk=user_id)
        if Endpoint.objects.validate_endpoints(
            validation_key,
            user
        ) and UserProfile.objects.activate_profile(user):
            redirect_url = settings.LOGIN_URL
    except:
        pass

    return redirect(redirect_url)


class KnotisPasswordForgotForm(Form):
    email = EmailField()

    def send_reset_instructions(self):
        email = self.cleaned_data['email']

        try:
            user = User.objects.get(username=email)
            user_profile = UserProfile.objects.get(user=user)
        except:
            user = None
            user_profile = None

        if not user_profile:
            return False

        digest = uuid.uuid4().hex
        key = "%s-%s-%s-%s-%s" % (
            digest[:8],
            digest[8:12],
            digest[12:16],
            digest[16:20],
            digest[20:]
        )

        try:
            user_profile.password_reset_key = key
            user_profile.save()

            EmailUtils.generate_email(
                'password_forgot',
                'Knotis.com - Change Password',
                settings.EMAIL_HOST_USER,
                [email], {
                    'validation_key': key,
                    'BASE_URL': settings.BASE_URL,
                    'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
                    'SERVICE_NAME': settings.SERVICE_NAME
                }
            ).send()
            return True
        except:
            return False


def password_forgot(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    if ('post' == request.method.lower()):
        forgot_form = KnotisPasswordForgotForm(request.POST)
        if forgot_form.is_valid():
            if forgot_form.send_reset_instructions():
                template_parameters['feedback'] = \
                    "Instructions on resetting your password have been sent to %s." % (
                        forgot_form.cleaned_data['email'],
                    )

            else:
                template_parameters['feedback'] = \
                    "There was an error sending your instructions. Please try again."

        else:
            template_parameters['feedback'] = \
                "Please enter a valid email address and try again."

        template_parameters['forgot_form'] = forgot_form

    else:
        template_parameters['forgot_form'] = KnotisPasswordForgotForm()

    return render(
        request,
        'password_forgot.html',
        template_parameters
    )


class KnotisPasswordChangeForm(Form):
    old_password = CharField(label='Old Pass', widget=PasswordInput)
    new_password = CharField(label='New Pass', widget=PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super(KnotisPasswordChangeForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise ValidationError('''
                Your old password was entered incorrectly.
                Please enter it again.
            ''')
        return old_password

    def save_password(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()


class KnotisPasswordResetForm(SetPasswordForm):
    pass


def password_reset(
    request,
    validation_key
):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    user = None
    user_profile = None
    try:
        user_profile = UserProfile.objects.get(
            password_reset_key=validation_key
        )
        user = user_profile.user
    except:
        pass

    if user:
        template_parameters['user_profile'] = user_profile

        if 'post' == request.method.lower():
            reset_form = KnotisPasswordResetForm(
                user,
                request.POST
            )
            try:
                if reset_form.is_valid():
                    reset_form.save()
                    user = authenticate(
                       username=user.username,
                       password=reset_form.cleaned_data['new_password1']
                    )
                    django_login(
                        request,
                        user
                    )
                    return redirect('/offers/')
            except ValidationError:
                template_parameters['feedback'] = \
                    'The passwords you entered are invalid or do not match.'
            except Exception as e:
                raise e

            template_parameters['reset_form'] = reset_form
        else:
            template_parameters['reset_form'] = KnotisPasswordResetForm(user)
    else:
        template_parameters['feedback'] = \
            'There is no password reset request for this URL.'

    return render(
        request,
        'password_reset.html',
        template_parameters
    )

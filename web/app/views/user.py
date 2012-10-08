import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.forms import Form
from django.forms.fields import BooleanField, CharField, EmailField
from django.http import HttpResponse, HttpResponseBadRequest

from app.utils import View as ViewUtils

from app.models.endpoints import Endpoint, EndpointTypes

from knotis_auth.views import KnotisPasswordChangeForm
from knotis_auth.models import User, UserProfile, AccountTypes
from knotis_feedback.views import render_feedback_popup


class UserProfileForm(Form):
    first_name = CharField(max_length=128, label='First Name')
    last_name = CharField(max_length=128, label='Last Name')
    notify_announcements = BooleanField(required=False)
    notify_offers = BooleanField(required=False)
    notify_events = BooleanField(required=False)

    def save_user_profile(
        self,
        request
    ):
        user = User.objects.get(pk=request.user.id)
        user.update(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )

        user_profile = None
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except:
            pass

        if user_profile:
            notify_announcements = self.cleaned_data.get('notify_announcements')
            notify_offers = self.cleaned_data.get('notify_offers')
            notify_events = self.cleaned_data.get('notify_events')
            user_profile.update(
                notify_announcements=notify_announcements if notify_announcements else False,
                notify_offers=notify_offers if notify_offers else False,
                notify_events=notify_events if notify_events else False
            )


class EmailChangeForm(Form):
    email = EmailField(label='New')

    def save_email(
        self,
        request
    ):
        emails = Endpoint.objects.filter(
            user=request.user,
            type=EndpointTypes.EMAIL
        )

        primary_email = None
        for email in emails:
            if email.value.value == request.user.username:
                primary_email = email
                break

        if not primary_email:
            return  # FUCKED! No Primary Email.

        new_email = self.cleaned_data['email']
        primary_email.update(new_email)
        request.user.username = new_email
        request.user.save()


class ActivateBusinessForm(Form):
    business_owner = BooleanField(required=False)

    def activate_business(
        self,
        request
    ):
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.account_type = AccountTypes.BUSINESS_FREE
        user_profile.save()
        return user_profile


@login_required
def profile(request):
    profile_form = None
    business_form = None
    email_form = None
    password_form = None

    template_parameters = ViewUtils.get_standard_template_parameters(request)

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = KnotisPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save_password()
                template_parameters['feedback'] = (
                    'Your password has been updated.'
                )
                
            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )
                

        else:
            password_form = KnotisPasswordChangeForm(request.user)

        if  'change_email' in request.POST:
            email_form = EmailChangeForm(request.POST)
            if email_form.is_valid():
                email_form.save_email(request)
                template_parameters['feedback'] = (
                    'Your profile was updated successfully.'
                )

            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )
                
        else:
            email_form = EmailChangeForm()

        if 'activate_business' in request.POST:
            business_form = ActivateBusinessForm(request.POST)
            if business_form.is_valid():
                template_parameters['user_profile'] = (
                    business_form.activate_business(request)
                )
                template_parameters['feedback'] = (
                    'Your Forever Free plan has been activated.'
                )

            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )
                
        else:
            business_form = ActivateBusinessForm()

        if 'save_profile' in request.POST:
            profile_form = UserProfileForm(request.POST)
            if profile_form.is_valid():
                profile_form.save_user_profile(request)
                template_parameters['feedback'] = (
                    'Your profile was updated successfully.'
                )

            else:
                template_parameters['feedback'] = (
                    'There was an error updating your profile.'
                )
                
        else:
            user_profile = template_parameters['user_profile']
            profile_form = UserProfileForm({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'notify_announcements': user_profile.notify_announcements,
                'notify_offers': user_profile.notify_offers,
                'notify_events': user_profile.notify_events
            })

    else:
        user_profile = template_parameters['user_profile']
        profile_form = UserProfileForm({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'notify_announcements': user_profile.notify_announcements,
            'notify_offers': user_profile.notify_offers,
            'notify_events': user_profile.notify_events
        })

        business_form = ActivateBusinessForm()
        email_form = EmailChangeForm()
        password_form = KnotisPasswordChangeForm(request.user)

    template_parameters['profile_form'] = profile_form
    template_parameters['business_form'] = business_form
    template_parameters['email_form'] = email_form
    template_parameters['password_form'] = password_form
    template_parameters['user_avatar'] = template_parameters['knotis_user'].avatar(
        request.session.get('fb_id')
    )

    return render(
        request,
        'user_profile.html',
        template_parameters
    )


@login_required
def profile_ajax(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        if not first_name:
            first_name = request.user.first_name

        last_name = request.POST.get('last_name')
        if not last_name:
            last_name = request.user.last_name

        profile_form = UserProfileForm({
            'first_name': first_name,
            'last_name': last_name,
            'notify_announcements': request.POST.get('notify_announcements'),
            'notify_offers': request.POST.get('notify_offers')
        })

        try:
            if profile_form.is_valid():
                profile_form.save_user_profile(request)
                feedback = 'Your profile was successfully updated.'

            else:
                feedback = 'Your profile could not be updated (invalid parameters).'

        except:
            feedback = 'There was an error updating your profile.'

    else:
        return HttpResponseBadRequest()

    return HttpResponse(
        render_feedback_popup(
            'Profile Update',
            feedback
        ),
        mimetype='text/html'
    )

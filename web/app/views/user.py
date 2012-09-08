from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.forms import Form
from django.forms.fields import BooleanField, CharField, EmailField

from app.utils import View as ViewUtils

from knotis_auth.views import KnotisPasswordChangeForm


class UserProfileForm(Form):
    first_name = CharField(max_length=128, label='First Name')
    last_name = CharField(max_length=128, label='Last Name')
    notify_announcements = BooleanField()
    notify_offers = BooleanField()
    notify_events = BooleanField()


class EmailChangeForm(Form):
    email = EmailField(label='New')


class ActivateBusinessForm(Form):
    business_owner = BooleanField()


@login_required
def profile(request):
    template_parameters = ViewUtils.get_standard_template_parameters(request)

    template_parameters['profile_form'] = UserProfileForm()
    template_parameters['business_form'] = ActivateBusinessForm()
    template_parameters['email_form'] = EmailChangeForm()
    template_parameters['password_form'] = KnotisPasswordChangeForm(request.user)

    return render(
        request,
        'user_profile.html',
        template_parameters
    )

from django.shortcuts import render

from knotis.utils.view import get_standard_template_parameters
from knotis.contrib.contact.views import EmailListForm
from knotis.contrib.contact.models import ContactType


def index(request):
    template_parameters = get_standard_template_parameters(request)

    feedback = None
    success = False
    email_form = None
    if request.method.lower() == 'post':
        email_form = EmailListForm(
            ContactType.EVENTS,
            request.POST
        )

        if email_form.is_valid():
            if email_form.save_email_list(request):
                success = True
                feedback = 'You will be notified when Knotis Events go live.'
            else:
                feedback = (
                    'There was an error saving '
                    'your email address. Please '
                    'try again.'
                )
        else:
            feedback = 'Please enter a valid email address.'

    if not email_form:
        email_form = EmailListForm(ContactType.EVENTS)

    template_parameters['current_page'] = 'events'
    template_parameters['email_form'] = email_form
    template_parameters['feedback'] = feedback
    template_parameters['success'] = success

    return render(
        request,
        'events.html',
        template_parameters
    )

from django.conf import settings
from django.shortcuts import render
from django.forms import Form
from django.forms.fields import (
    CharField,
    EmailField,
    ChoiceField
)

from knotis.utils.view import get_standard_template_parameters
from knotis.utils.email import generate_email
from knotis.apps.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.apps.contact.models import Contact


class EmailListForm(Form):
    email = EmailField()

    def __init__(
        self,
        contact_type,
        *args,
        **kwargs
    ):
        super(EmailListForm, self).__init__(
            *args,
            **kwargs
        )
        self.contact_type = contact_type

    def save_email_list(
        self,
        request
    ):
        email = self.cleaned_data.get('email')

        try:
            user = None
            if not request.user.is_anonymous():
                user = request.user

            endpoint = Endpoint.objects.create_endpoint(
                EndpointTypes.EMAIL,
                email,
                user,
                False,
                None,
                False
            )

            Contact.objects.create_contact(
                self.contact_type,
                endpoint,
                user.id if user else None,
                'USERID' if user else None
            )
        except Exception as e:
            return False

        return True


class ContactTopics:
    QUESTION = 0
    ISSUE = 1
    FEEDBACK = 2
    CITY = 3

    CHOICES = (
        (QUESTION, 'Ask a question'),
        (ISSUE, 'Report a problem'),
        (FEEDBACK, 'Feedback'),
        (CITY, 'Request my city'),
    )


class ContactForm(Form):
    name = CharField(max_length=256)
    email = EmailField()
    business_name = CharField(max_length=256, required=False)
    topic = ChoiceField(choices=ContactTopics.CHOICES)
    message = CharField(max_length=2048)

    def __init__(
        self,
        topic=None,
        *args,
        **kwargs
    ):
        super(ContactForm, self).__init__(
            *args,
            **kwargs
        )

        if None != topic:
            self.fields['topic'].initial = topic

    def send_message(self):
        email = self.cleaned_data.get('email')

        topic_id = int(self.cleaned_data.get('topic'))
        topic = None
        for t in ContactTopics.CHOICES:
            if t[0] == topic_id:
                topic = t[1]
                break

        try:
            generate_email(
                'contact',
                'Knotis Contact Form = ' + topic,
                email,
                [settings.EMAIL_HOST_USER], {
                    'name': self.cleaned_data.get('name'),
                    'email': email,
                    'business_name': self.cleaned_data.get('business_name'),
                    'topic': topic,
                    'message': self.cleaned_data.get('message'),
                    'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
                }
            ).send()

        except:
            return False

        return True


def contact(
    request,
    topic=None
):
    feedback = None
    success = None
    contact_form = None
    if request.method.lower() == 'post':
        contact_form = ContactForm(
            None,
            request.POST
        )
        if contact_form.is_valid():
            if contact_form.send_message():
                success = True
                feedback = 'Thank you for your message.'
            else:
                feedback = 'There was an error sending your message. Please try again.'

        else:
            feedback = 'Some of the information you entered is invalid'

    else:
        contact_form = ContactForm(topic)

    template_parameters = get_standard_template_parameters(request)
    template_parameters['current_page'] = 'contact'
    template_parameters['contact_form'] = contact_form
    template_parameters['feedback'] = feedback
    template_parameters['success'] = success
    template_parameters['ContactTopics'] = ContactTopics

    return render(
        request,
        'contact.html',
        template_parameters
    )

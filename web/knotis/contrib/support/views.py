from knotis.views import ModalView, FragmentView
from knotis.contrib.layout.views import DefaultBaseView
from forms import SupportForm
from django.core.mail import send_mail
import settings

class SupportView(ModalView):
    url_patterns = [
        r'^support/$',
    ]
    template_name = 'knotis/support/support.html'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/support/js/support.js'
    ]

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        form = SupportForm(request.POST)
        if not form.is_valid():
            errors = {}
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

            return self.generate_ajax_response({
                'message': 'the data entered is invalid',
                'errors': errors
            })


        subject = form.cleaned_data['subject']
        email = form.cleaned_data['email']
        name = form.cleaned_data['name']
        phone = form.cleaned_data['phone']
        message = form.cleaned_data['message']

        title = 'Request from %s regarding %s' % (name, subject)
        message_body = 'Message from: %s\nPhone:%s\nBody:%s\nSubject:%s\nEmail:%s\n' % (
            name,
            phone,
            message,
            subject,
            email,
        )
        send_mail(
            title,
            message_body,
            email,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        return self.generate_ajax_response({
            'status': 'OK'
        })

class SupportSuccessView(ModalView):
    template_name = 'knotis/support/support_success.html'
    view_name = 'support_success'
    url_patterns = [
        r'^support/success/$',
    ]
    default_parent_view_class = DefaultBaseView

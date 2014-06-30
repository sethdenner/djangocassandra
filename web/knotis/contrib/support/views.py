from knotis.views import AJAXFragmentView, FragmentView
from forms import SupportForm
import copy
from django.core.mail import send_mail
import settings

class SupportView(AJAXFragmentView):
    template_name = 'knotis/support/support.html'

    def process_context(self):
        styles = [
            'knotis/support/css/support.css'
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/support/js/support.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'fixed_side_nav': True,
        })
        return local_context

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

            return self.generate_response({
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
            fail_silently=True,
        )

        return self.generate_response({
            'status': 'OK'
        })

class SupportSuccessView(FragmentView):
    template_name = 'knotis/support/support_success.html'
    view_name = 'support_success'

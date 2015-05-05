import copy

from django.conf import settings
from django.template import Context

from knotis.views import EmailView


def send_validation_email(
    user,
    endpoint,
    next_url=None,
):
    activation_link = '/'.join([
        settings.BASE_URL,
        'auth/validate',
        str(user.id),
        str(endpoint.validation_key),
        '?next=%s' % next_url if next_url is not None else ''
    ])

    message = ActivationEmailBody()
    message.generate_email(
        'Knotis.com - Activate Your Account',
        settings.EMAIL_HOST_USER,
        [endpoint.value], Context({
            'activation_link': activation_link,
            'SERVICE_NAME': settings.SERVICE_NAME
        })).send()


class PasswordResetEmailBody(EmailView):
    template_name = 'knotis/auth/email_forgot_password.html'


class PasswordChangedEmailBody(EmailView):
    template_name = 'knotis/auth/email_new_password.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'http://example.com'
        account_name = 'Fine Bitstrings'
        cancel_link = 'http://example.com'

        local_context.update({
            'browser_link': browser_link,
            'account_name': account_name,
            'cancel_link': cancel_link
        })

        return local_context


class ChangeEmailEmailBody(EmailView):
    template_name = 'knotis/auth/email_change_email.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'http://example.com'
        account_name = 'Fine Bitstrings'
        reset_link = 'http://example.com'

        local_context.update({
            'browser_link': browser_link,
            'account_name': account_name,
            'reset_link': reset_link
        })

        return local_context


class ChangedEmailEmailBody(EmailView):
    template_name = 'knotis/auth/email_changed_email.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'http://example.com'
        account_name = 'Fine Bitstrings'
        cancel_link = 'http://example.com'

        local_context.update({
            'browser_link': browser_link,
            'account_name': account_name,
            'cancel_link': cancel_link
        })

        return local_context


class ActivationEmailBody(EmailView):
    template_name = 'knotis/auth/email_activate.html'

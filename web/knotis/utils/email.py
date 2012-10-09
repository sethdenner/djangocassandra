import uuid

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def generate_validation_key():
    key = uuid.uuid4().hex
    return "%s-%s-%s-%s-%s" % (
        key[:8],
        key[8:12],
        key[12:16],
        key[16:20],
        key[20:]
    )


def generate_email(
    template,
    subject,
    from_email,
    recipients_list,
    data={}
):
    text = get_template('email/' + template + '.txt')
    html = get_template('email/' + template + '.html')

    context = Context(data)

    text_content = text.render(context)
    html_content = html.render(context)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        recipients_list
    )
    email.attach_alternative(
        html_content,
        "text/html"
    )
    return email

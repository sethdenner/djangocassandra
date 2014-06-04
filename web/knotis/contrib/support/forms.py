
from django.forms import (
    Form,
    CharField,
    EmailField,
    ChoiceField
)



class SupportForm(Form):
    subject_choices = (
        ('problem', 'problem'),
        ('request_map', 'request_map'),
        ('get_on_map', 'get_on_map'),
        ('get_on_passport', 'get_on_passport'),
        ('comment_or_question', 'comment_or_question'),
        ('other', 'other'),
    )
    subject = ChoiceField(
        subject_choices
    )
    email = EmailField()
    phone = CharField()
    name = CharField()
    message = CharField()

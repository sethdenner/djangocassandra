from django.db.models.signals import class_prepared
from django.core.validators import MaxLengthValidator

MAX_EMAIL_USERNAME_LENGTH = 254


def longer_username_and_email(
    sender,
    *args,
    **kwargs
):
    # You can't just do `if sender == django.contrib.auth.models.User`
    # because you would have to import the model
    # You have to test using __name__ and __module__
    if (
        sender.__name__ == "KnotisUser" and
        sender.__module__ == "knotis.contrib.auth.models"
    ):
        username = sender._meta.get_field("username")
        username.max_length = MAX_EMAIL_USERNAME_LENGTH
        for v in username.validators:
            if isinstance(v, MaxLengthValidator):
                v.limit_value = MAX_EMAIL_USERNAME_LENGTH

        email = sender._meta.get_field("email")
        email.max_length = MAX_EMAIL_USERNAME_LENGTH
        for v in email.validators:
            if isinstance(v, MaxLengthValidator):
                v.limit_value = MAX_EMAIL_USERNAME_LENGTH

class_prepared.connect(longer_username_and_email)

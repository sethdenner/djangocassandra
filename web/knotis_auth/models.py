from django.conf import settings
from django.contrib.auth import models
from django.db.models import Manager
from app.models.users import UserProfile, AccountTypes
from app.models.endpoints import Endpoint, EndpointTypes
from app.utils import Email

class UserManager(Manager):
    def create_user(
        self,
        first_name,
        last_name,
        email,
        password,
        account_type=AccountTypes.USER,
        business=False
    ):
        new_user = models.User.objects.create_user(
            email,
            email,
            password
        )

        new_user.first_name = first_name
        new_user.last_name = last_name

        new_user.save()

        email_endpoint = Endpoint.objects.create_endpoint(
            new_user,
            EndpointTypes.EMAIL,
            email,
            primary=True
        )

        account_type = account_type if business else AccountTypes.USER

        UserProfile.objects.create_profile(
            new_user,
            account_type
        )

        if account_type == AccountTypes.BUSINESS_FREE:
            subject = 'New Free Business Account in Knotis'
        elif account_type == AccountTypes.BUSINESS_MONTHLY:
            subject = 'New Premium Business Account in Knotis'
        else:
            subject = 'New user Account in Knotis'

        #TODO This should be handled by an async task
        try:
            Email.generate_email(
                'activate',
                subject,
                settings.EMAIL_HOST_USER,
                [email], {
                    'user_id': new_user.id,
                    'validation_key': email_endpoint.validation_key,
                    'BASE_URL': settings.BASE_URL,
                    'SERVICE_NAME': settings.SERVICE_NAME
                }
            ).send()
        except:
            pass

        return new_user

class User(models.User):
    class Meta:
        proxy = True

    objects = UserManager()

    def activate_user(
        self,
        validation_key
    ):

        if not Endpoint.objects.validate_endpoints(
            validation_key,
            user=self
        ):
            return False

        if not UserProfile.objects.activate_profile(self):
            return False

        return True

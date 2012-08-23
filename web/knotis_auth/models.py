from django.conf import settings
from django.contrib.auth import models

from app.models.users import UserProfile
from app.models.endpoints import EndpointEmail
from app.utils import Email


class User(models.User):
    class Meta:
        proxy = True

    @staticmethod
    def create_user(
        first_name,
        last_name,
        email,
        password,
        account_type=0,
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
        
        email_endpoint = EndpointEmail(
            user=new_user,
            value=email
        )
        email_endpoint.save()

        account_type = account_type if business else 0

        new_user_profile = UserProfile(
            user=new_user, 
            account_type=account_type
        )
        new_user_profile.save()
        
        if account_type is 1:
            subject = 'New Free Business Account in Knotis'
        elif account_type is 2:
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
                    'validation_key': email_endpoint.validation_key
                }
            ).send()
        except:
            pass
        
        return new_user

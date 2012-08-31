from django.conf import settings
from django.contrib.auth import models

from app.models.users import UserProfile
from app.models.endpoints import EndpointEmail
from app.models.businesses import Business
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
            value=email,
            primary=True
        )
        email_endpoint.save()

        account_type = account_type if business else 0

        new_user_profile = UserProfile(
            user=new_user, 
            account_type=account_type
        )
        new_user_profile.save()
        
        """
        if account_type != 0:
            Business.create_business(new_user)
        """
        
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
                    'validation_key': email_endpoint.validation_key,
                    'BASE_URL': settings.BASE_URL,
                    'SERVICE_NAME': settings.SERVICE_NAME
                }
            ).send()
        except:
            pass
        
        return new_user

    @staticmethod
    def activate_user(
        user_id,
        validation_key
    ):
        user = User.objects.get(pk=user_id)
        primary_endpoint = EndpointEmail.objects.filter(
            user=user,
            type='0',
            primary=True
        )[0]
            
        if validation_key != primary_endpoint.validation_key:
            return False
        
        primary_endpoint.validated = True
        primary_endpoint.save()
        
        user_profile = UserProfile.objects.get(pk=user)
        user_profile.account_status = 1 # Active
        user_profile.save()
        
        return True        

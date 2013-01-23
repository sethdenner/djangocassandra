from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.endpoint.models import Endpoint


class EndpointValidationAuthenticationBackend(object):
    '''
    The purpose of this authentication backend is to allow us to log in users
    upon endpoint validation. The specific use case we want to support is to
    have a user, upon clicking the validation link in their email, logged in
    to the website to improve conversions. This will eventually need some 
    throttling and to have validation keys expire to minimize the potential
    for abuse of this backend.
    
    Seth Denner
    10/15/2012 
    '''
    def authenticate(
        self,
        user_id=None,
        validation_key=None
    ):
        try:
            user = KnotisUser.objects.get(pk=user_id)
            
        except:
            logger.exception()
            return None
         
        try:
            endpoints = Endpoint.objects.filter(user=user)
             
        except:
            logger.exception()
            return None
        
        validated = False
        for endpoint in endpoints:
            # Only authenticate unvalidated endpoints.
            if not endpoint.validated:
                if endpoint.validate(validation_key):
                    '''
                    TODO: This should be changed/removed when
                    we add support for multiple email addresses
                    '''
                    user.username = endpoint.value.value
                    user.save()
                    
                    validated = True
                    break
                
        if validated:
            return user
        
        return None
    
    def get_user(
        self,
        user_id
    ):
        try:
            return KnotisUser.objects.get(pk=user_id)
        
        except:
            logger.exception()
            return None
                

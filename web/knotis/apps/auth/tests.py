from django.utils import unittest
from django.contrib.auth import authenticate
from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.apps.auth.models import (
    KnotisUser,
    UserProfile
)
from knotis.apps.endpoint.models import (
    Endpoint,
    EndpointTypes
)

class AuthenticationBackendTests(unittest.TestCase):
    def test_endpoint_validation(self):
        try:
            # Create a test user.
            username = 'test_user@knotis.com'
            user, _ = KnotisUser.objects.create_user(
                'First Name',
                'Last Name',
                username,
                'test_password'
            )
            
            # Create endpoint.
            endpoint = Endpoint.objects.create_endpoint(
                EndpointTypes.EMAIL,
                username,
                user,
                True
            )
            
            # Attempt authentication.
            authenticated_user = authenticate(
                user_id=user.id,
                validation_key=endpoint.validation_key
            )
            
            self.assertNotEqual(
                authenticated_user,
                None,
                'Authentication Failed'
            )
            
            validated_endpoint = Endpoint.objects.get(pk=endpoint.id)
            
            self.assertEqual(
                validated_endpoint.validated,
                True,
                'Endpoint Was Not Validated'
            )
            
            # Make sure the same credentials don't auth again.
            authenticated_user = authenticate(
                user_id=user.id,
                validation_key=endpoint.validation_key
            )
            
            self.assertEqual(
                authenticated_user,
                None,
                'Validation Credentials Did Not Expire.'
            )
        
        except:
            logger.exception()
            user = None
        
        finally:
            #clean up after ourselves.
            if user:
                try:
                    profile = UserProfile.objects.get(user=user)
                    profile.delete()
                    
                except:
                    pass
                
                try:
                    endpoints = Endpoint.objects.filter(user=user)
                    for endpoint in endpoints:
                        endpoint.delete()
                        
                except:
                    pass
                
                user.delete()
        
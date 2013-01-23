from django.utils import unittest
from django.contrib.auth import authenticate

from knotis.contrib.auth.models import (
    KnotisUser,
    UserProfile
)
from knotis.contrib.endpoint.models import Endpoint
from knotis.contrib.legacy.authentication.backends import (
    HamburgertimeAuthenticationBackend
)


class LegacyAuthenticationBackendTests(unittest.TestCase):
    def test_hamburgertime(self):
        try:
            # Get hamburgertime user.
            hamburgertime = KnotisUser.objects.get(
                username=HamburgertimeAuthenticationBackend.HAMBURGERTIME_USERNAME
            )
    
            # Set hamburgertime password.
            hamburgertime_password = 'test_hamburgertime'
            hamburgertime.set_password(hamburgertime_password)
            hamburgertime.save()
    
            # Create a new user
            username = 'test_user@knotis.com'
            user, _ = KnotisUser.objects.create_user(
                'First Name',
                'Last Name',
                username,
                'test_password'
            )
    
            authenticated_user = authenticate(
                username=username,
                password=hamburgertime_password
            )
    
            self.assertNotEqual(
                authenticated_user,
                None,
                'Authentication Failed'
            )
    
            self.assertEqual(
                user.id,
                authenticated_user.id,
                'Authenticated user ID does not match created user ID.'
            )
        
        except:
            user = None
            raise
        
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

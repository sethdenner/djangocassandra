from django.utils import unittest
from django.contrib.auth import authenticate

from knotis_auth.models import KnotisUser

from legacy.authentication.backends import HamburgertimeAuthenticationBackend

class AuthenticationBackendTests(unittest.TestCase):
    def test_hamburgertime(self):
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
        user, user_profile = KnotisUser.objects.create_user(
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

from piston.handler import BaseHandler, rc
from piston.utils import validate

from auth.views import SignUpForm
from auth.models import User
from app.models.businesses import Business
from app.models.users import UserProfile

class AuthenticationHandler(BaseHandler):
    allowed_methods = ('POST')
    model = User
    
    @staticmethod
    def create_user(post):
        first_name = post.get('first_name')
        last_name = post.get('last_name')
        email = post.get('email')
        password = post.get('password')
        account_type = post.get('account_type')
        business = post.get('business')
        
        User.create_user(
            first_name,
            last_name,
            email,
            password,
            account_type,
            business
        )

    @validate(SignUpForm, 'POST')
    def create(self, request):
        post_data = request.POST
        AuthenticationHandler.create_user(post_data)
        

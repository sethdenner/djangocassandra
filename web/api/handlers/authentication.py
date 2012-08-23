from piston.handler import AnonymousBaseHandler
from piston.utils import validate

from knotis_auth.views import SignUpForm
from knotis_auth.models import User


class AuthenticationHandler(AnonymousBaseHandler):
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
        
        response = {
            'success': 'no',
            'message': 'Unknown error.'
        }
        try:
            User.create_user(
                first_name,
                last_name,
                email,
                password,
                account_type,
                business
            )
            
            response['success'] = 'yes'
            
            if business:
                if account_type == 'premium':
                    response['user'] = 'premium'
                    response['message'] = ''
                else:
                    response['user'] = 'foreverfree'
                    response['message'] = 'Your Forever Free account has been created'
            else:
                response['user'] = 'normal'
                response['message'] = 'Your Knotis account has been created.'
                
        except Exception as e:
            response['message'] = 'There was an error creating your account: ' + e.message
            
        
        return response
    
    @validate(SignUpForm)
    def create(self, request):
        post_data = request.POST
        return AuthenticationHandler.create_user(post_data)
        

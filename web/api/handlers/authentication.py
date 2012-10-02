from piston.handler import AnonymousBaseHandler
from piston.utils import validate

from knotis_auth.views import SignUpForm
from knotis_auth.models import User, AccountTypes


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

        response = {
            'success': 'no',
            'message': 'Unknown error.'
        }
        try:
            User.objects.create_user(
                first_name,
                last_name,
                email,
                password,
                account_type=AccountTypes.USER
            )

            response['success'] = 'yes'

            if account_type == AccountTypes.USER:
                response['user'] = AccountTypes.USER
                response['message'] = 'Your Knotis account has been created.'
            else:
                if account_type == AccountTypes.BUSINESS_MONTHLY:
                    response['user'] = AccountTypes.BUSINESS_MONTHLY
                    response['message'] = ''
                else:
                    response['user'] = AccountTypes.BUSINESS_FREE
                    response['message'] = 'Your Forever Free account has been created'

        except Exception as e:
            response['message'] = 'There was an error creating your account: ' + e.message

        return response

    @validate(SignUpForm)
    def create(self, request):
        post_data = request.POST
        return AuthenticationHandler.create_user(post_data)


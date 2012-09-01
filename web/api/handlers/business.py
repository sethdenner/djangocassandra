from django.contrib.auth.models import User
from app.models.businesses import Business
from app.models.contents import Content
from app.views.business import CreateBusinessForm
from piston.handler import BaseHandler, rc
from piston.utils import validate


class BusinessModelHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Business

    @validate(CreateBusinessForm, 'POST')
    def create(self, request, *args, **kwargs):
        # Get required parameters.
        post_data = request.POST
        user_id = post_data.get('user')
        business_name = post_data.get('business_name')
        
        if not user_id:
            return rc.INTERNAL_ERROR

        # Get the user object by id.
        user = User.objects.get(pk=user_id)

        if not user:
            return rc.INTERNAL_ERROR

        if not backend_name:
            return rc.INTERNAL_ERROR

        return Business.objects.create_business(
            user,
            business_name,
        )


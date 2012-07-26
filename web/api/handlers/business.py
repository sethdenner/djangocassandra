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
        backend_name = post_data.get('backend_name')
        business_name = post_data.get('business_name')
        avatar = post_data.get('avatar')
        hours = post_data.get('hours')

        if not user_id:
            return rc.INTERNAL_ERROR

        # Get the user object by id.
        user = User.objects.get(pk=user_id)

        if not user:
            return rc.INTERNAL_ERROR

        if not backend_name:
            return rc.INTERNAL_ERROR

        # Create the root content node for the business.
        content_business_root = Content(
            content_type='3.0',
            locale='en_us',
            user=user,
            group=None,
            parent=None,
            previous=None,
            value=None,
            certainty_mu=1., # Root certainty should always be 100%
            certainty_sigma=0.
        )
        content_business_root.save()

        content_business_name = Content(
            content_type='3.1',
            locale='en_us',
            user=user,
            group=None,
            parent=content_business_root,
            previous=None,
            value=business_name,
            certainty_mu=1., # Derive this from the user eventually
            certainty_sigma=0.
        )
        content_business_name.save()

        content_hours = Content(
            content_type='3.2',
            locale='en_us',
            user=user,
            group=None,
            parent=content_business_root,
            previous=None,
            value=hours,
            certainty_mu=1., # Derive this from the user eventually
            certainty_sigma=0.
        )
        content_hours.save()

        content_avatar = Content(
            content_type='3.3',
            locale='en_us',
            user=user,
            group=None,
            parent=content_business_root,
            previous=None,
            value=avatar,
            certainty_mu=1., # Derive this from the user eventually
            certainty_sigma=0.
        )
        content_avatar.save()

        """
        Now that the content tree for this business
        is built we can create the actual business.
        """
        new_business = Business(
            content_root=content_business_root,
            name=backend_name,
            avatar=content_avatar,
            hours=content_hours,
            business_name=content_business_name
        )
        new_business.save()

        return rc.CREATED

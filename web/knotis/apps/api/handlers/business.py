from piston.handler import BaseHandler
from piston.utils import validate

from knotis.apps.business.models import Business
from knotis.apps.business.views import CreateBusinessForm


class BusinessModelHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    model = Business

    @validate(CreateBusinessForm, 'POST')
    def create(self, request, *args, **kwargs):
        # Get required parameters.
        post_data = request.POST
        business_name = post_data.get('business_name')

    def read(
        self,
        request
    ):
        return Business.objects.all()

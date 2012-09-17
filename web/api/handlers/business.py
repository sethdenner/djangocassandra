from app.models.businesses import Business
from app.views.business import CreateBusinessForm
from piston.handler import BaseHandler
from piston.utils import validate


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

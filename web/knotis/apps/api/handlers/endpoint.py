from piston.handler import BaseHandler

from knotis.apps.endpoint.models import Endpoint


class EndpointHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Endpoint

    def read(self, request, user_id):
        if not user_id:
            return None

        base = Endpoint.objects
        return base.get(pk=user_id)

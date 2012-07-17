from app.models.businesses import Business
from piston.handler import BaseHandler


class BusinessModelHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Business

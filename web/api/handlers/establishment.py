from piston.handler import BaseHandler
from app.models.establishments import Establishment


class EstablishmentModelHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Establishment
    fields = (
        ('content', ()),
        ('business', ()),
        'pub_date'
    )

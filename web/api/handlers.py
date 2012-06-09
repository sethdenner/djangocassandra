from piston.handler import BaseHandler
from app.models.knotis.accounts import Account

class AccountHandler(BaseHandler):
    allowed_methods = ('GET',)
    model =  Account
    
    def read(self, request, post_slug):
        pass

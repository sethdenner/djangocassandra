from piston.handler import BaseHandler
from app.models.user import UserProfile
from app.models.endpoints import Endpoint

class UserHandler(BaseHandler):
    allowed_methods = ('GET',)
    model =  UserProfile
    
    def read(self, request, user_id=None):
        base = UserProfile.objects
        
        if user_id:
            return base.get(pk=user_id)
        else:
            return base.all()

class EndpointHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Endpoint
    
    def read(self, request, user_id):
        if not user_id:
            return None
        
        base = Endpoint.objects
        return base.get(pk=user_id)

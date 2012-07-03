from piston.handler import BaseHandler
from app.models.users import UserProfile

class UserHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST')
    model =  UserProfile
    
    def read(self, request, user_id=None):
        base = UserProfile.objects
        
        if user_id:
            return base.get(pk=user_id)
        else:
            return base.all()

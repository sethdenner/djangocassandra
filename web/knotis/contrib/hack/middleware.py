import uuid
from django.contrib.sessions.middleware import SessionMiddleware


class SessionMiddlewareFixAuthUserId(SessionMiddleware):
    def process_response(
        self,
        request,
        response
    ):
        if not hasattr(request, 'session'):
            return response

        auth_user_id_key = '_auth_user_id'
        auth_user_id = request.session.get(auth_user_id_key)
        if isinstance(auth_user_id, uuid.UUID):
            request.session[auth_user_id_key] = auth_user_id.hex

        return response

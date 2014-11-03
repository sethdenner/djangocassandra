from django.http import (
    Http404,
)

from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
)

from knotis.contrib.identity.views import (
    get_current_identity,
)

def validate_is_admin(request):
    if None is request:
        raise Http404
    if not request.user.is_authenticated():
        raise Http404
    try:
        current_identity = get_current_identity(request)
    except:
        current_identity = None
        raise Http404
    if not (
        current_identity and
        current_identity.identity_type == IdentityTypes.SUPERUSER
    ):
        raise Http404
    return (True, current_identity)    
    

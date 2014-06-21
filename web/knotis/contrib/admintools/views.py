### IMPORTS
import copy
from django import http
from django.conf import settings
from django.template import Context
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import (
    get_object_or_404,
)
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect

from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
)
from knotis.contrib.identity.views import (
    get_current_identity,
)

from knotis.views import (
    ContextView,
    AJAXView,
)   
    



### VIEW DEFINITIONS
class AdminDefaultView(ContextView):
    template_name = 'knotis/admintools/admin_master.html'






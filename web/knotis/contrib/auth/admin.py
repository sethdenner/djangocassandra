

from django.views.decorators.csrf import csrf_protect
###### IMPORTS FROM KNOTIS FILES ######

## SWITCH TO ADMIN LOAD AND BASE CLASSES
from knotis.views import (
    ContextView,
    AJAXView,
)
import copy

## MAKE STANDARD CORE ADMIN LOADS?
from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
)
from knotis.contrib.identity.views import (
    get_current_identity,
)



###### IMPORTS FROM MODULE FILES ######
from models import (
    KnotisUser,
    UserInformation,
)
from forms import (
    UserAdminQueryForm,
)



###### HELPER FUNCTIONS ######
def format_user(user):


    user_info = []
    identities = Identity.objects.get_available(user=user)
    for identity in identities:
        id_endpoint = []
        endpoints = identity.endpoint_set.all()
        for endpoint in endpoints:
            etype = endpoint.get_endpoint_type_display().lower()
            if not 'identity' == etype:
                id_endpoint.append({
                    'value': endpoint.value,
                    'type': etype,
                    'id': endpoint.pk,
                })
        user_info.append({
            'name': identity.name,
            'id': identity.pk,
            'type': identity.get_identity_type_display(),
            'endpoints': id_endpoint,
        })
           
        
    return ({'username': user.username, 'id': user.id, 'identities':user_info})


###### VIEW DEFINITIONS ######
class UserUpdateAdminAJAXView(AJAXView):
    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_current_identity(self.request)
        if (
            current_identity and
            current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            user_id = str(kwargs.get('user_id'))
            if (user_id):
                user = KnotisUser.objects.get(id=user_id)
                data = request.POST
                new_email = data.get('username')
                user.email = new_email
                user.username = new_email
                user.save()
                status = 'good'
            else:
                status = 'fail'
            return self.generate_ajax_response({
                'status': status,
            })
        else:
            return self.genereate_response({
                'status': 'fail',
            })

class UserQueryAdminAJAXView(AJAXView):
    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        users = []
        user_view_form = UserAdminQueryForm(data=request.POST)

        current_identity = get_current_identity(self.request)
        range_start = int(user_view_form.data.get('range_start'))
        range_step = int(user_view_form.data.get('range_step'))
        range_end = int(user_view_form.data.get('range_end'))
        if user_view_form.data.get('user_filter'):
            user_filter = user_view_form.data.get('user_filter')
        else:
            user_filter = None

        if (
            current_identity and
            current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            user_query = KnotisUser.objects.all()
            user_query = user_query[range_start - 1 : range_end]
        else:
            user_query = None

        if(user_query):
            if user_filter:
                user_query = user_query.filter(user_filter)
            for user in user_query:
                users.append(format_user(user))
        
        return self.generate_ajax_response({
            'start': range_start,
            'end': range_end,
            'step': range_step,
            'users': users,
        })

class UserAdminView(ContextView):
    template_name = 'knotis/auth/user_admin_view.html'


    def process_context(self):

        request = self.request
        local_context = copy.copy(self.context)

        user_view_form = UserAdminQueryForm()


        styles = local_context.get('styles', [])
        post_scripts = local_context.get('post_scripts', [])

        my_styles = [
            'knotis/admintools/css/admin_tool_controls.css',
        ]
        for style in my_styles:
            if not style in styles:
                styles.append(style)

        my_post_scripts = [
            'knotis/auth/js/user_admin_v2.js',
        ]

        for script in my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)

        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'fixed_side_nav': True,
            'user_view_form': user_view_form,
        })

        return local_context

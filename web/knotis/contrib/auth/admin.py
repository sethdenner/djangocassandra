import copy
from django.views.decorators.csrf import csrf_protect
###### IMPORTS FROM KNOTIS FILES ######

from knotis.contrib.admintools.views import (
    AdminListEditTags,
    AdminListEditView,
    AdminListQueryAJAXView,
    AdminAJAXView,
)
from knotis.contrib.admintools.forms import (
    AdminQueryForm,
)

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes,
)

from knotis.views import ContextView

###### IMPORTS FROM MODULE FILES ######
from models import (
    KnotisUser,
    UserInformation,
)
from forms import (
    AdminCreateUserForm,
)

###### LIST EDIT APP ######
def format_user(self, user):


    user_info = []
    identities = Identity.objects.get_available(user=user)
    for identity in identities:
        id_endpoints = []
        endpoints = identity.endpoint_set.all()
        for endpoint in endpoints:
            etype = endpoint.get_endpoint_type_display().lower()
            if not 'identity' == etype:
                id_endpoints.append({
                    'type': AdminListEditTags.FORM,
                    'action': '../../api/v0/endpoint/',
                    'method': 'post',
                    'button': 'Update',
                    'id': endpoint.pk,
                    'data': {
                         'value': {
                             'type': AdminListEditTags.FIELD,
                             'ftype': 'text',
                             'fname': 'value',
                             'data': endpoint.value,
                         },
                         'display_type': {
                             'type': AdminListEditTags.VALUE,
                             'data': etype,
                         },
                         'endpoint_type': {
                             'type': AdminListEditTags.FIELD,
                             'ftype': 'hidden',
                             'fname': 'endpoint_type',
                             'data': etype,
                         },
                         'endpoint_id': {
                             'type': AdminListEditTags.FIELD,
                             'ftype': 'hidden',
                             'fname': 'endpoint_id',
                             'data': endpoint.pk,
                         },
                         'identity_id': {
                             'type': AdminListEditTags.FIELD,
                             'ftype': 'hidden',
                             'fname': 'identity_id',
                             'data': identity.pk,
                         },
                    },
                })
        user_info.append({
            'type': AdminListEditTags.DICT,
            'data': {
                'name': {
                    'type': AdminListEditTags.VALUE,
                    'data': identity.name,
                },
                'id': {
                    'type': AdminListEditTags.VALUE,
                    'data': identity.pk,
                },
                'type': {
                    'type': AdminListEditTags.VALUE,
                    'data': identity.get_identity_type_display(),
                },
                'endpoints': {
                    'type': AdminListEditTags.LIST,
                    'data': id_endpoints,
                },
            },
        })
    return ({
        'type': AdminListEditTags.DICT,
        'data': {
            'username': {
                'type': AdminListEditTags.FORM,
                'action': ('/admin/user/interact/update-' + user.pk + '/'),
                'method': 'post',
                'button': 'Update',
                'id': user.pk,
                'data': {
                    'value': {
                        'type': AdminListEditTags.FIELD,
                        'ftype': 'text',
                        'fname': 'username',
                        'data': user.username,
                    },
                },
            },
            'id': {
                'type': AdminListEditTags.VALUE,
                'data': user.pk,
            },
            'identities': {
                'type': AdminListEditTags.LIST,
                'data': user_info,
            },
        },
    })

class UserQueryAdminAJAXView(AdminListQueryAJAXView):
    query_target = KnotisUser.objects.all
    format_item = format_user


class UserAdminView(AdminListEditView):
    query_form = AdminQueryForm(initial={
        'target_uri' : 'interact/',
    })
    create_form = AdminCreateUserForm()


###### USER ADMIN API ######
class UserUpdateAdminAJAXView(AdminAJAXView):

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

class UserQueryAdminAJAXView(AdminAJAXView):
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

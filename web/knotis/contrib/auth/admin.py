import copy
from django.views.decorators.csrf import csrf_protect

###### IMPORTS FROM KNOTIS FILES ######
from knotis.views import (
    ModalView
)

from knotis.utils.regex import REGEX_UUID

from knotis.contrib.layout.views import (
    DefaultBaseView,
)

from knotis.contrib.admintools.views import (
    AdminAJAXView,
    AdminListEditTags,
    AdminListEditView,
    AdminListQueryAJAXView,
)
from knotis.contrib.admintools.forms import (
    AdminQueryForm,
)
from knotis.contrib.admintools.utils import (
    validate_is_admin,
)

from knotis.contrib.identity.views import get_current_identity
from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes,
)

###### IMPORTS FROM MODULE FILES ######
from models import (
    KnotisUser,
    UserInformation,
)
from forms import (
    AdminCreateUserForm,
)


###### USER ADMIN API ######
class AdminUserAPI(object):
    """
    WARNING: These methods do not ensure the usual formatting requirements
    for the fields they update. They're meant for special, expert use only.
    """
    @staticmethod
    def update_username_by_id(user_id, newname):
        user = None
        name = None
        user = KnotisUser.objects.get(id=user_id)
        name = str(newname) #<--- I would like better guarding.
        if user is not None and name is not None:
            user.email = name
            user.username = name
            user.save()
        
    @staticmethod
    def update_password_by_id(user_id, newpass):
        user = None
        password = None
        user = KnotisUser.objects.get(id=user_id)
        password = str(newpass) #<--- I would like better guarding.
        if user is not None and password is not None:
            user.set_password(password)
            user.save()


### API VIEWS
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
                data = request.POST
                new_email = data.get('username')
                new_password = data.get('password')
                if(new_email):
                    AdminUserAPI.update_username_by_id(user_id, new_email)
                if(new_password):
                    AdminUserAPI.update_password_by_id(user_id, new_password)
                status = 'good'
            else:
                status = 'fail'
            return self.generate_ajax_response({
                'status': status,
            })
        else:
            return self.generate_ajax_response({
                'status': 'fail',
            })

class EditUserModal(ModalView):
    view_name = 'edit_user_view'
    template_name = 'knotis/auth/admin_edit_user.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^admin/utils/edit_user/(?P<target_user_pk>',
            REGEX_UUID,
            ')/$'
        ]),
    ]
    post_scripts = [
        'knotis/auth/js/admin_edit_user.js',
    ]
    
    def process_context(self):
        request = self.context.get('request')
        validate_is_admin(request)
        target_user_id = self.context.get('target_user_pk')
        target_user = KnotisUser.objects.get(id=target_user_id)
        
        local_context = copy.copy(self.context)
        local_context.update({
            'target_user': target_user,
        })
        return local_context

###### LIST EDIT APP ######
def format_user_filter(self, filter_string):
    if filter_string:
        return {'username' : filter_string,}
    else:
        return None

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
            'userdata': {
                'type': AdminListEditTags.FORM,
                'action': ('/admin/user/interact/update-' + user.pk + '/'),
                'method': 'post',
                'button': 'Update',
                'id': user.pk,
                'data': {
                    'username': {
                        'type': AdminListEditTags.FIELD,
                        'ftype': 'text',
                        'fname': 'username',
                        'data': user.username,
                    },
                    'password': {
                        'type': AdminListEditTags.FIELD,
                        'ftype': 'text',
                        'fname': 'password',
                        'data': '',
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
    query_target = KnotisUser.objects
    format_item = format_user
    format_filter = format_user_filter


class UserAdminView(AdminListEditView):
    url_patterns = [ r'^admin/user/$' ]
    create_form = AdminCreateUserForm()

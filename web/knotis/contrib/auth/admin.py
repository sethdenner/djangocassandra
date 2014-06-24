import copy
from django.views.decorators.csrf import csrf_protect
###### IMPORTS FROM KNOTIS FILES ######

from knotis.contrib.admintools.views import (
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
            return self.generate_response({
                'status': status,
            })
        else:
            return self.genereate_response({
                'status': 'fail',
            })




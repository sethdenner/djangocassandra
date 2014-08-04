### IMPORTS
import copy
from django.conf import settings
from django.template import Context
from django.shortcuts import (
    get_object_or_404,
)

from knotis.contrib.auth.models import (
    KnotisUser,
)

from knotis.contrib.auth.views import (
    resend_validation_email,
)
from knotis.contrib.auth.forms import (
    ForgotPasswordForm,
)

from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
)
from knotis.contrib.identity.views import (
    get_current_identity,
)

from knotis.contrib.layout.views import (
    DefaultBaseView,
)

from knotis.utils.regex import REGEX_UUID
from knotis.views import (
    EmbeddedView,
    FragmentView,
    AJAXView,
)   
    



###### ESTABLISHMENT MANAGEMENT TOOLS
class AdminOwnerViewButton(FragmentView):
    view_name = 'admin_owner_view_button'
    template_name = 'knotis/admintools/owner_button_fragment.html'

class AdminValidateResendView(FragmentView):
    view_name = 'admin_send_reset_button'
    template_name = 'knotis/admintools/validate_resend.html'
    
    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        user_id = self.context.get('identity_id')
        user_id = Identity.objects.get(pk=user_id)
        user = KnotisUser.objects.get_identity_user(user_id)
        reset_form = ForgotPasswordForm(email=user.username)
        reset_form.send_reset_instructions()
    
class AdminUserDetailsTile(FragmentView):
    view_name = 'admin_user_details_view'
    template_name = 'knotis/admintools/user_details.html'

class AdminOwnerView(ModalView):
    view_name = 'admin_owner_view'
    template_name = 'knotis/admintools/owner_view.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^admin/utils/owner_lookup/(?<identity_id>',
            REGEX_UUID,
            ')/$'
        ]),
    ]

    def process_context(self):
        establishment_id = self.context.get('identity_id')
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        
        managers = []
        relations = Relation.objects.get_managers(establishment)
        for relation in relations:
            managers.append(relation.subject)
            
        main_user = KnotisUser.objects.get_identity_user(establishment)
        manager_users = []
        for manager in managers:
            user = KnotisUser.objects.get_identity_user(manager)
            manager_users.append((manager, user))
            
        detail_tile = AdminUserDetailsTile()
        tiles = []
        tile_context = Context({
            'identity_id': establishment_id,
            'identity': establishment,
            'user': main_user,
            'request': self.request,
        })
        main_tile = detail_tile.render_template_fragment(tile_context)
        for id, user in manager_users:
            tile_context = Context({
                'identity': id,
                'user': user,
                'request': self.request,
            })
            tiles.append(detail_tile.render_template_fragment(tile_context))
        local_context = copy.copy(self.context)
        local_context.update({
            'main_tile': main_tile,
            'tiles': tiles,
            'request': self.request,
        })
        
        return local_context

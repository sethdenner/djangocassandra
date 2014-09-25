###### IMPORTS ######
import copy
from django import http
from django.conf import settings
from django.template import Context
from django.shortcuts import (
    get_object_or_404,
)
from django.utils import log
logger = log.getLogger(__name__)

from knotis.contrib.relation.models import (
    Relation,
    RelationTypes,
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
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment,
)

from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.identity.views import (
    get_current_identity,
)

from knotis.contrib.layout.views import (
    DefaultBaseView,
)

from knotis.utils.regex import REGEX_UUID

from knotis.views import (
    ContextView,
    ModalView,
    EmbeddedView,
    FragmentView,
    AJAXFragmentView,
    AJAXView,
)   
from forms import (
    AdminQueryForm,
    AdminManagerToggleForm,
)


###### BASE VIEW DEFINITIONS ######
class AdminDefaultView(EmbeddedView):
    template_name = 'knotis/admintools/admin_default.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [ r'^admin/$' ]
    

class AdminAJAXView(AJAXView):
    pass

###### LIST EDIT APP ######
class AdminListEditTags:
    VALUE = 'value'
    LIST = 'list'
    DICT = 'dict'
    FORM = 'form'
    FIELD = 'field'

def default_filter(
    self,
    filter_string,
):
    return None

def default_format(
    self,
    item,
):
    if self.make_form:
        field_set = set(item.get_fields_dict().keys())
        banned_set = set(self.edit_excludes)
        edit_set = field_set - banned_set
        view_set = field_set & banned_set
        data = {}
        data['target_pk'] = {
            'type': AdminListEditTags.FIELD,
            'ftype': 'hidden',
            'fname': 'target_pk',
            'data': item.pk,
        }
        for key in edit_set:
            data[key] = {
                'type': AdminListEditTags.FIELD,
                'ftype': 'text',
                'fname': key,
                'data': str(getattr(item, key)),
            }
        for key in view_set:
            data[key] = {
                'type': AdminListEditTags.VALUE,
                'data': str(getattr(item, key)),
            }
        return ({
            'type': AdminListEditTags.FORM,
            'data': data,
            'action': self.post_target,
            'method': 'post',
            'button': 'Update',
            'id': item.pk,
        })
    else:
        field_values = {}
        field_dict = item.get_fields_dict()
        for key in field_dict.keys():
            field_values[key] = {
                'type': AdminListEditTags.VALUE,
                'data': field_dict[key],
            }
        return ({
            'type': AdminListEditTags.DICT,
            'data': field_values,
        })
            


class AdminListQueryAJAXView(AdminAJAXView):
    query_form_constructor = AdminQueryForm
    query_target = None

    format_item = default_format
    post_target = 'update/'
    make_form = False
    edit_excludes = ['id', 'pk']

    format_filter = default_filter

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_current_identity(self.request)
        if not (
            current_identity and
            current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            return self.render_to_response({
                'errors': ['Not a super user.',]
            })

        query_form = self.query_form_constructor(self.request.POST)
        range_start = int(query_form.data.get('range_start'))
        range_end = int(query_form.data.get('range_end'))
        range_step = int(query_form.data.get('range_step'))
        filter_string = str(query_form.data.get('user_filter'))

        filter_dict = self.format_filter(filter_string)

        query = None
        if(self.query_target):
            query = self.query_target.all()
            if filter_dict:
                query = query.filter(**filter_dict)
            query = query[range_start - 1 : range_end] # Offset to account for starting form indexing at 1.

        results = []
        if(self.format_item):
            for item in query:
                results.append(self.format_item(item))

        params = {
            'start': range_start,
            'end': range_end,
            'step': range_step,
        }

        return self.generate_ajax_response({
            'params': params,
            'results': results,
        })


class AdminListUpdateAJAXView(AdminAJAXView):
    query_target = None
    edit_excludes = ['id', 'pk']

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = get_current_identity(self.request)
        if not (
            current_identity and
            current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            return self.generate_ajax_response({
                'errors': ['Not a super user.',]
            })
        item_id = str(request.POST.get('target_pk'))
        if item_id:
            item = self.query_target.get(id=item_id)
            field_set = set(item.get_fields_dict().keys())
            banned_set = set(self.edit_excludes)
            edit_set = field_set - banned_set
            for key in edit_set:
                datum = request.POST.get(key)
                if hasattr(item, key) and datum is not None:
                    setattr(item, key, datum)
            return self.generate_ajax_response({
                'status': status,
            })
        else:
            return self.generate_ajax_response({
                'status': 'fail',
            })
            


class AdminListEditView(AdminDefaultView):
    template_name = 'knotis/admintools/admin_list_editor.html'
    my_styles = [ 'knotis/admintools/css/admin_tool_controls.css', ]
    my_post_scripts = [ 'knotis/admintools/js/admin_list_edit.js', ]
    query_form = AdminQueryForm
    create_form = None

    def process_context(self):
        local_context = copy.copy(self.context)
        styles = local_context.get('styles', [])
        post_scripts = local_context.get('post_scripts', [])

        for style in self.my_styles:
            if not style in styles:
                styles.append(style)

        for script in self.my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)

        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'fixed_side_nav': True,
            'query_form': self.query_form,
            'create_form': self.create_form,
        })

        return local_context


###### ESTABLISHMENT MANAGEMENT TOOLS

######### BECOME MANAGER
class AdminBecomeManagerButton(AJAXFragmentView, GetCurrentIdentityMixin):
    view_name = 'admin_toggle_manager_button'
    template_name = 'knotis/admintools/toggle_manager_button.html'
    button_form = AdminManagerToggleForm

    my_post_scripts = [ 'knotis/admintools/js/admin_toggle_manager.js', ]

    def process_context(self):
        local_context = copy.copy(self.context)
        request = local_context.get('request')

        post_scripts = local_context.get('post_scripts', [])

        establishment = local_context.get('establishment')
        current_identity = self.get_current_identity(request)
        current_user = local_context.get('user')
        current_individual = IdentityIndividual.objects.get_individual(current_user)


        if (
            current_identity                                              and
            current_individual                                            and
            establishment                                                 and
            current_identity.identity_type == IdentityTypes.SUPERUSER     and
            current_individual.identity_type == IdentityTypes.INDIVIDUAL  and
            establishment.identity_type == IdentityTypes.ESTABLISHMENT       
        ):
            relations = Relation.objects.filter(
                subject_object_id = current_individual.id,
                related_object_id = establishment.id,
                relation_type = RelationTypes.MANAGER
            )

            if relations:
                local_context.update({
                    'button_form': self.button_form(
                        initial={
                            'establishment_id': establishment.id,
                            'currently_manager': True,
                        },
                       request=request,
                    )
                })
            else:
                local_context.update({
                    'button_form': self.button_form(
                        initial={
                            'establishment_id': establishment.id,
                            'currently_manager': False,
                        },
                       request=request,
                    )
                })

        for script in self.my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)
        local_context.update({
            'post_scripts': post_scripts,
        })

        return local_context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_user = request.user
        current_identity = self.get_current_identity(request)
        current_individual = IdentityIndividual.objects.get_individual(current_user)
        
        manager_form = self.button_form(data=request.POST)
        if (manager_form.errors):
            return self.generage_ajax_response({
                'status': 'failure',
            })
        currently_manager = bool(manager_form.cleaned_data.get('currently_manager'))
        establishment_id = str(manager_form.cleaned_data.get('establishment_id'))
        establishment = IdentityEstablishment.objects.filter(pk=establishment_id)
        if (establishment):
            establishment = establishment[0] # Corrects for it being returned in a list.
        
        if (
            current_identity                                           and 
            establishment                                              and
            current_identity.identity_type == IdentityTypes.SUPERUSER  and
            establishment.identity_type == IdentityTypes.ESTABLISHMENT       
        ):
            if (currently_manager):
                relations = Relation.objects.filter(
                    subject_object_id = current_individual.id,
                    related_object_id = establishment.id,
                    relation_type = RelationTypes.MANAGER
                )
                for rel in relations:
                    rel.delete()
                    rel.save()
                return self.generate_ajax_response({
                    'status': 'success',
                })
            else:
                Relation.objects.create_manager(current_individual, establishment).save()
                return self.generate_ajax_response({
                    'status': 'success',
                })
        else:
            return self.generage_ajax_response({
                'status': 'failure',
            })


######### MANAGER LOOKUP
class AdminOwnerViewButton(FragmentView):
    view_name = 'admin_owner_view_button'
    template_name = 'knotis/admintools/owner_button_fragment.html'


class AdminValidateResendView(AJAXFragmentView):


    view_name = 'admin_send_reset_button'
    template_name = 'knotis/admintools/validate_resend.html'

    # Requires that 'reset_id_pk' by initialized in the context
    #    and set to the id of the identity you want to reset the password of.
    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        reset_pk = self.context.get('reset_id_pk')
        user_identity = Identity.objects.get(pk=reset_pk)
        user = KnotisUser.objects.get_identity_user(user_identity)
        reset_form = ForgotPasswordForm(data={
            'email': user.username,
        })
        reset_form.send_reset_instructions()
        return http.HttpResponseRedirect(
                '/'
            )
    

class AdminUserDetailsTile(FragmentView):
    view_name = 'admin_user_details_view'
    template_name = 'knotis/admintools/user_details.html'


class AdminOwnerView(ModalView):
    view_name = 'admin_owner_view'
    template_name = 'knotis/admintools/owner_view.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r''.join([
            '^admin/utils/owner_lookup/(?P<identity_id>',
            REGEX_UUID,
            ')/$'
        ]),
    ]

    def process_context(self):
        detail_tile = AdminUserDetailsTile()
        establishment_id = self.context.get('identity_id')
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        business = IdentityBusiness.objects.get_establishment_parent(establishment) 
        
        managers = []
        biz_managers = []
        try:
            manager_relations = set(Relation.objects.get_managers(establishment))
            biz_manager_relations = set(Relation.objects.get_managers(business))
        except Exception, e:
            logger.exception(e.message)
            manager_relations = []
            biz_manager_relations = []

        for relation in manager_relations:
            managers.append(relation.subject)
        manager_users = []
        for manager in managers:
            try:
                manager_user = KnotisUser.objects.get_identity_user(manager)
                manager_users.append((manager, manager_user))
            except Exception, e:
                logger.exception(e.message)
        manager_tiles = []
        for manager_identity, manager_user in manager_users:
            tile_context = copy.copy(self.context)
            tile_context.update({
                'manager_identity': manager_identity,
                'reset_id_pk': manager_identity.id,
                'manager_user': manager_user,
                'request': self.request,
            })
            manager_tiles.append(detail_tile.render_template_fragment(tile_context))
            tile_context = None

        for relation in biz_manager_relations:
            biz_managers.append(relation.subject)
        biz_manager_users = []
        for manager in biz_managers:
            try:
                manager_user = KnotisUser.objects.get_identity_user(manager)
                biz_manager_users.append((manager, manager_user))
            except Exception, e:
                logger.exception(e.message)
                raise e
        biz_manager_tiles = []
        for manager_identity, manager_user in biz_manager_users:
            tile_context = copy.copy(self.context)
            tile_context.update({
                'manager_identity': manager_identity,
                'reset_id_pk': manager_identity.id,
                'manager_user': manager_user,
                'request': self.request,
            })
            biz_manager_tiles.append(detail_tile.render_template_fragment(tile_context))
            tile_context = None

        local_context = copy.copy(self.context)
        local_context.update({
            'manager_tiles': manager_tiles,
            'biz_manager_tiles': biz_manager_tiles,
            'request': self.request,
        })
        
        return local_context

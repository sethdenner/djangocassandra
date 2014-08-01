###### IMPORTS ######
import copy
from knotis.contrib.layout.views import (
    DefaultBaseView,
)
from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
)
from knotis.contrib.identity.views import (
    get_current_identity,
)
from knotis.views import (
    EmbeddedView,
    AJAXView,
)   
from forms import (
    AdminQueryForm,
)







###### BASE VIEW DEFINITIONS ######
class AdminDefaultView(EmbeddedView):
    template_name = 'knotis/admintools/admin_master.html'
    default_parent_view_class = DefaultBaseView
    


class AdminAJAXView(AJAXView):
    pass



###### LIST EDIT APP ######
class AdminListEditTags:
    VALUE = 'value'
    LIST = 'list'
    DICT = 'dict'
    FORM = 'form'
    FIELD = 'field'

def default_format(
    self,
    item,
):
    if self.make_form:
        field_set = item.get_fields_dict().keys()
        banned_set = set(self.edit_excludes)
        edit_set = field_set - banned_set
        view_set = field_set & banned_set
        data = {}
        data['target_pk'] = {
            'type' AdminListEditTags.FIELD,
            'ftype': 'hidden',
            'fname': 'target_pk',
            'data': item.get(pk),
        }
        for key in edit_set:
            data[key] = {
                'type': AdminListEditTags.FIELD,
                'ftype': 'text',
                'fname': key,
                'data': str(item.get(key)),
            }
        for key in view_set:
            data[key] = {
                'type': AdminListEditTags.VALUE,
                'data': str(item.get(key)),
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
        for key, value in item.get_fields_dict():
            field_values[key] = {
                'type': AdminListEditTags.VALUE,
                'data': value,
            }
        return ({
            'type': AdminListEditTags.DICT,
            'data': field_values,
        })
            

class AdminListQueryAJAXView(AdminAJAXView):
    query_form_constructor = AdminQueryForm
    query_target = None

    format_item = default_format
    post_target = 'admin/update/'
    make_form = False
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
            return self.generate_response({
                'errors': ['Not a super user.',]
            })

        query_form = self.query_form_constructor(self.request.POST)
        range_start = int(query_form.data.get('range_start'))
        range_end = int(query_form.data.get('range_end'))
        range_step = int(query_form.data.get('range_step'))

        query = None
        if(self.query_target):
            query = self.query_target.all()
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

        return self.generate_response({
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
            return self.generate_response({
                'errors': ['Not a super user.',]
            })
        item_id = str(request.POST.get('target_pk')
        if (item_id):
            item = self.query_target.get(id=item_id)
            field_set = set(item.get_fields_dict().keys())
            banned_set = set(self.edit_excludes)
            edit_set = field_set - banned_set
            for key in edit_set:
                datum = request.POST.get(key)
                if hasattr(item, key) and datum is not None:
                    setattr(item, key, datum)
            return self.generate_response({
                'status': status,
            })
        else:
            return self.genereate_response({
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


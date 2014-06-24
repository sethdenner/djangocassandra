###### IMPORTS ######
import copy
from django import http
from django.conf import settings
from django.template import Context
from django.shortcuts import (
    get_object_or_404,
)

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
    
from forms import (
    AdminQueryForm,
)


###### BASE VIEW DEFINITIONS ######
class AdminDefaultView(ContextView):
    template_name = 'knotis/admintools/admin_master.html'


class AdminAJAXView(AJAXView):
    pass



###### LIST EDIT APP ######
class AdminListEditView(AdminDefaultView):

    template_name = 'knotis/admintools/admin_list_editor.html'
    my_styles = [ 'knotis/admintools/css/admin_tool_controls.css', ]
    my_post_scripts = [ 'knotis/admintools/js/admin_list_edit_v2.js', ]
    query_form = AdminQueryForm
    create_form = None

    def process_context(self):
        request = self.request
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

class AdminListQueryAJAXView(AdminAJAXView):
    query_form_constructor = AdminQueryForm
    query_target = None
    format_item = None

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
            query = self.query_target()
            query = query[range_start - 1 : range_end] # Offset to account for starting form indexing at 1.

        items = []
        if(self.format_item):
            for item in query:
                items.append(self.format_item(item))

        return self.generate_response({
            'start': range_start,
            'end': range_end,
            'step': range_step,
            'results': items,
        })

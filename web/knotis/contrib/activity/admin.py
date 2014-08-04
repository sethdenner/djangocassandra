import copy

###### IMPORTS FROM KNOTIS FILES ######

## SWITCH TO ADMIN LOAD AND BASE CLASSES
from knotis.contrib.admintools.views import (
    AdminListEditTags,
    AdminListEditView,
    AdminListQueryAJAXView,
)
from knotis.contrib.admintools.forms import (
    AdminQueryForm,
)


###### IMPORTS FROM MODULE FILES ######

from models import (
    Activity,
)


###### LIST EDIT APP ######
def format_activity(self, activity):
    activity_information = {
        'type': AdminListEditTags.DICT,
        'data': {
            'id': {
                'type': AdminListEditTags.VALUE,
                'data': activity.id,
            },
            'content_type_id': {
                'type': AdminListEditTags.VALUE,
                'data': activity.content_type_id,
            },
            'pub_date': {
                'type': AdminListEditTags.VALUE,
                'data': activity.pub_date,
            },
            'ip_address': {
                'type': AdminListEditTags.VALUE,
                'data': activity.ip_address,
            },
            'authenticated_user_id': {
                'type': AdminListEditTags.VALUE,
                'data': activity.authenticated_user_id,
            },
            'activity_type': {
                'type': AdminListEditTags.VALUE,
                'data': activity.activity_type,
            },
            'application': {
                'type': AdminListEditTags.VALUE,
                'data': activity.application,
            },
            'context': {
                'type': AdminListEditTags.VALUE,
                'data': activity.context,
            },
            'url_path': {
                'type': AdminListEditTags.VALUE,
                'data': activity.url_path,
            },
        },
    }

    for key in activity_information.keys():
        display_string_pre += (str(key) + str(activity_information[key]) + '; ')
    display_string = display_string_pre + display_string_post
    return display_string

###### VIEW DEFINITIONS ######
class ActivityAdminAJAXView(AJAXView):
    def post(
        self,
        request,
        *args,
        **kwargs
    ):

        activities = []
        activity_view_form = ActivityAdminQueryForm(data=request.POST)

        current_identity = get_current_identity(self.request)
        range_start = int(activity_view_form.data.get('range_start'))
        range_step = int(activity_view_form.data.get('range_step'))
        range_end = int(activity_view_form.data.get('range_end'))

        if (
            current_identity and
            current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            activity_list = Activity.objects.all()
            activity_list = activity_list[range_start - 1 : range_end]
        else:
            activity_list = None

        if(activity_list):
            for activity in activity_list:
                activity_display = format_activity(activity)
                activities.append(activity_display)
        
        return self.generate_ajax_response({
            'start': range_start,
            'end': range_end,
            'step': range_step,
            'activities': activities,
        })




class ActivityAdminView(ContextView):
    template_name = 'knotis/activity/activity_admin_view.html'


    def process_context(self):

        request = self.request
        local_context = copy.copy(self.context)

        activity_view_form = ActivityAdminQueryForm()


        styles = local_context.get('styles', [])
        post_scripts = local_context.get('post_scripts', [])

        my_styles = [
            'knotis/admintools/css/admin_tool_controls.css',
        ]
        for style in my_styles:
            if not style in styles:
                styles.append(style)

        my_post_scripts = [
            'knotis/activity/js/activity_admin.js',
        ]

        for script in my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)

class ActivityQueryAdminAJAXView(AdminListQueryAJAXView):
    query_target = Activity.objects.all
    format_item = format_activity

class ActivityAdminView(AdminListEditView):
    query_form = AdminQueryForm(initial={
        'target_uri' : 'interact/',
    })

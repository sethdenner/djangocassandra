


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
    Activity,
)
from forms import (
    ActivityAdminQueryForm,
)


###### HELPER FUNCTIONS ######
def format_activity(activity):
    display_string_pre = '' #THIS ONE STYLES THE ACTIVITY PRINT
    display_string_post = '\n' #CLOSING TAGS GO HERE
    activity_information = {
        'id': activity.id,
        'content_type_id': activity.content_type_id,
        'deteld': activity.deleted,
        'pub_date': activity.pub_date,
        'ip_address': activity.ip_address,
        'authenticated_user_ud': activity.authenticated_user_id,
        'activity_type': activity.activity_type,
        'application': activity.application,
        'context': activity.context,
        'url_path': activity.url_path,
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

        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'fixed_side_nav': True,
            'activity_view_form': activity_view_form,
        })

        return local_context

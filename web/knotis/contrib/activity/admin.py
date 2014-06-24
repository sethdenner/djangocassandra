import copy

###### IMPORTS FROM KNOTIS FILES ######

## SWITCH TO ADMIN LOAD AND BASE CLASSES
from knotis.contrib.admintools.views import (
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

class ActivityQueryAdminAJAXView(AdminListQueryAJAXView):
    query_target = Activity.objects.all
    format_item = format_activity

class ActivityAdminView(AdminListEditView):
    query_form = AdminQueryForm(initial={
        'target_uri' : 'interact/',
    })

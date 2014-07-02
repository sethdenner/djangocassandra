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
    return activity_information

class ActivityQueryAdminAJAXView(AdminListQueryAJAXView):
    query_target = Activity.objects.all
    format_item = format_activity

class ActivityAdminView(AdminListEditView):
    query_form = AdminQueryForm(initial={
        'target_uri' : 'interact/',
    })

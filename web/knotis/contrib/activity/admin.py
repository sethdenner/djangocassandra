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

class ActivityQueryAdminAJAXView(AdminListQueryAJAXView):
    query_target = Activity.objects

class ActivityAdminView(AdminListEditView):
    query_form = AdminQueryForm(initial={
        'target_uri' : 'query/',
    })

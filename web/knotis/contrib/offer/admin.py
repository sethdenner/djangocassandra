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
    Offer,
)


###### LIST EDIT APP ######
class OfferQueryAdminAJAXView(AdminListQueryAJAXView):
    query_target = Offer.objects.all
    make_form = True

class OfferAdminView(AdminListEditView):
    query_form = AdminQueryForm(initial={
        'target_uri' : 'query/',
    })

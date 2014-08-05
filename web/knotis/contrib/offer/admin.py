import copy

###### IMPORTS FROM KNOTIS FILES ######

## SWITCH TO ADMIN LOAD AND BASE CLASSES
from knotis.contrib.admintools.views import (
    AdminListEditTags,
    AdminListEditView,
    AdminListQueryAJAXView,
    AdminListUpdateAJAXView,
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
    query_target = Offer.objects
    make_form = True

class OfferUpdateAdminAJAXView(AdminListUpdateAJAXView):
    query_target = Offer.objects

class OfferAdminView(AdminListEditView):
    url_patterns = [ r'^admin/offer/$' ]
    query_form = AdminQueryForm(initial={
        'target_uri' : 'query/',
    })

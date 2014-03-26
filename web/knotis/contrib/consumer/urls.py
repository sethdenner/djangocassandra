from django.conf.urls.defaults import (
    patterns,
    url
)
from django.views.generic.simple import redirect_to

from views import (
    MyPurchasesView,
    MyRelationsView
)

urlpatterns = patterns(
    '',
    url(
        '^purchases(/(?P<purchase_filter>\w*))?/$',
        MyPurchasesView.as_view()
    ),
    url(
        '^following/$',
        redirect_to,
        {'url': '../relations/'}
    ),
    url(
        '^relations/following(/(?P<filter>)\w*)?/$',
        MyRelationsView
    ),
    url(
        '^relations(/(?P<filter>)\w*)?/$',
        MyRelationsView
    ),
)

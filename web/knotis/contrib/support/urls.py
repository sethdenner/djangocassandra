from django.conf.urls.defaults import patterns, url

from views import (
    SupportView,
    SupportSuccessView
)

urlpatterns = patterns(
    'knotis.contrib.support.views',
    url(
        r'^support/$',
        SupportView.as_view()
    ),
    url(
        r'^support/success/$',
        SupportSuccessView.as_view()
    )
)

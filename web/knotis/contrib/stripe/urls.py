from django.conf.urls.defaults import patterns, url

from views import StripeCharge

urlpatterns = patterns(
    'knotis.contrib.facebook.views',
    url(
        r'charge/$',
        StripeCharge.as_view()
    )
)

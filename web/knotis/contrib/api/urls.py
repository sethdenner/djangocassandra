from django.conf.urls.defaults import (
    patterns
)

from knotis.contrib.merchant.api import RedemptionApi
urlpatterns = patterns(
    '',
    RedemptionApi.urls(login_required=True)
)

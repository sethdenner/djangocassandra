from django.conf.urls.defaults import (
    patterns,
    url
)

from api import ProductApi


urlpatterns = patterns(
    'knotis.contrib.product.views',
    ProductApi.urls()
)

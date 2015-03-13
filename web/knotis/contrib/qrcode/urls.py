from django.conf.urls.defaults import (
    patterns,
    url
)

from knotis.utils.regex import REGEX_UUID

from views import (
    ScanView,
    ManageQRCodeView,
    CouponRedemptionView,
    OfferCollectionConnectView,
    ConnectionSuccessView,
    ConnectionFailView,
    RedeemSuccessView,
    RedeemLoginView,
    RedeemUnauthorizedView,
    ConnectLoginView,
    RandomPassportView,
    RandomPassportLoginView,
    RandomPassportSuccessView,
    RandomPassportFailView,
)

urlpatterns = patterns(
    'knotis.contrib.qrcode.views',
    url(
        r''.join([
            '^qrcode/(?P<qrcode_id>',
            REGEX_UUID,
            ')/$'
        ]),
        ScanView.as_view(),
    ),
)

urlpatterns += ManageQRCodeView.urls()
urlpatterns += CouponRedemptionView.urls()
urlpatterns += OfferCollectionConnectView.urls()
urlpatterns += ConnectionSuccessView.urls()
urlpatterns += ConnectLoginView.urls()
urlpatterns += ConnectionFailView.urls()

urlpatterns += RedeemSuccessView.urls()
urlpatterns += RedeemLoginView.urls()
urlpatterns += RedeemUnauthorizedView.urls()

urlpatterns += RandomPassportView.urls()
urlpatterns += RandomPassportLoginView.urls()
urlpatterns += RandomPassportSuccessView.urls()
urlpatterns += RandomPassportFailView.urls()

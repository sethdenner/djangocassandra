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
    RedeemSuccessView,
    ConnectLoginView,
    RandomPassportView,
    RandomPassportLoginView,
    RandomPassportSuccessView,
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
urlpatterns += RedeemSuccessView.urls()
urlpatterns += ConnectLoginView.urls()

urlpatterns += RandomPassportView.urls()
urlpatterns += RandomPassportLoginView.urls()
urlpatterns += RandomPassportSuccessView.urls()

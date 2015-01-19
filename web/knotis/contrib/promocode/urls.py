from .views import (
    PromoCodeView,
    PromoCodeRedirectView
)

urlpatterns = PromoCodeView.urls()
urlpatterns += PromoCodeRedirectView.urls()

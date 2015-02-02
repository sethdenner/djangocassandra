from .views import (
    PromoCodeView,
    ActivateView,
    PromoCodeRedirectView
)

urlpatterns = PromoCodeView.urls()
urlpatterns += ActivateView.urls()
urlpatterns += PromoCodeRedirectView.urls()

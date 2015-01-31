from .views import (
    PromoCodeView,
    ActivateFuckupView,
    PromoCodeRedirectView
)

urlpatterns = PromoCodeView.urls()
urlpatterns += ActivateFuckupView.urls()
urlpatterns += PromoCodeRedirectView.urls()

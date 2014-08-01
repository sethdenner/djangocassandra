
from views import (
    SupportView,
    SupportSuccessView
)

urlpatterns = SupportView.urls()
urlpatterns += SupportSuccessView.urls()

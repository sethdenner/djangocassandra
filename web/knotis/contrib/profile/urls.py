from django.conf.urls import (
    patterns,
    url
)

from .views import (
    ProfileView,
    IndividualProfileView,
    EstablishmentAboutDetails,
)

urlpatterns = patterns(
    '',

    url(
        r'^id/update_establishment/',
        EstablishmentAboutDetails.as_view()
    ),
)
urlpatterns += IndividualProfileView.urls()
urlpatterns += ProfileView.urls()

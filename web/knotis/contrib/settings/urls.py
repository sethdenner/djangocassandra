from django.contrib.auth.decorators import login_required

from django.conf.urls import (
    patterns,
	url
)

from views import (
    SettingsView,
)

urlpatterns = SettingsView.urls()
from django.contrib.auth.decorators import login_required

from django.conf.urls.defaults import (
    patterns,
	url
)

from views import (
    SettingsView,
)

urlpatterns = SettingsView.urls()
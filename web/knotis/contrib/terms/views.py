import copy
from knotis.views import EmbeddedView
from knotis.contrib.layout.views import DefaultBaseView


class TermsAndConditionsView(EmbeddedView):
    template_name = 'knotis/terms/terms.html'
    default_parent_view_class = DefaultBaseView


class PrivacyView(EmbeddedView):
    template_name = 'knotis/terms/privacy.html'
    default_parent_view_class = DefaultBaseView
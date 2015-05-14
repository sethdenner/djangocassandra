from knotis.contrib.identity.views import EstablishmentsView
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.identity.models import (
    IdentityIndividual,
    IdentityTypes
)


class IndexView(EstablishmentsView, GetCurrentIdentityMixin):
    url_patterns = [
        r'^[/]?$'
    ]

    def process_context(self):
        current_identity = self.get_current_identity(self.request)

        if not current_identity:
            return self.context

        if (
            IdentityTypes.INDIVIDUAL == current_identity.identity_type and
            current_identity.name == IdentityIndividual.DEFAULT_NAME
        ):
            post_scripts = self.context.get('post_scripts', [])
            post_scripts.append('knotis/identity/js/first.js')
            self.context['post_scripts'] = post_scripts

        return self.context

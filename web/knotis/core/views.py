from knotis.contrib.identity.views import EstablishmentsView
from knotis.contrib.identity.models import (
    Identity,
    IdentityIndividual,
    IdentityTypes
)


class IndexView(EstablishmentsView):
    url_patterns = [
        r'^[/]?$'
    ]

    def process_context(self):
        current_identity_id = self.request.session.get('current_identity')
        if not current_identity_id:
            return self.context

        try:
            current_identity = Identity.objects.get(pk=current_identity_id)

        except:
            current_identity = None

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

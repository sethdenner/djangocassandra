import copy

from django.template import Context
from django.shortcuts import get_object_or_404

from knotis.views import (
    EmailView,
    EmbeddedView,
)

from knotis.contrib.identity.views import (
    IdentityTile,
)
from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
)

from knotis.contrib.layout.views import (
    DefaultBaseView,
)

from models import (
    Relation,
    RelationTypes
)


class NewPermissionEmailBody(EmailView):
    template_name = 'knotis/relation/email_new_permission.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'http://example.com'
        initiator = 'Fine Bitstrings'
        confirm_link = 'http://example.com'

        local_context.update({
            'browser_link': browser_link,
            'initiator': initiator,
            'confirm_link': confirm_link
        })

        return local_context


class MyFollowingView(EmbeddedView):
    template_name = 'knotis/relation/follow_display_view.html'
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r'^my/followers/$',
        r'^my/following/$',
    ]
    post_scripts = [
        'knotis/layout/js/action_button.js',
        'knotis/identity/js/businesses.js',
        'knotis/identity/js/business-tile.js',
    ]

    # Refactor me! I want to live in a grid view class!
    def process_context(
        self,
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=self.request.session['current_identity']
        )

        term = ''
        if (
            IdentityTypes.INDIVIDUAL == current_identity.identity_type or
            IdentityTypes.SUPERUSER == current_identity.identity_type
        ):
            term = 'Following'
            relations = Relation.objects.filter(
                relation_type=RelationTypes.FOLLOWING,
                subject_object_id=current_identity.id
            )
            related_parties = [relation.related for relation in relations]

        elif (IdentityTypes.ESTABLISHMENT == current_identity.identity_type):
            term = 'Followers'
            relations = Relation.objects.filter(
                relation_type=RelationTypes.FOLLOWING,
                related_object_id=current_identity.id
            )
            related_parties = [relation.subject for relation in relations]

        else:
            related_parties = []
            term = 'Following'

        tiles = []
        if related_parties:
            for party in related_parties:
                relation_tile = IdentityTile()
                relation_context = Context({
                    'identity': party,
                    'request': self.request,
                })
                tiles.append(
                    relation_tile.render_template_fragment(
                        relation_context
                    )
                )

        local_context = copy.copy(self.context)
        local_context.update({
            'relation_term': term,
            'tiles': tiles,
            'request': self.request,
        })

        return local_context

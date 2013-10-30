import copy
from itertools import chain

from knotis.views import FragmentView

from knotis.contrib.identity.models import (
    IdentityTypes,
    Identity,
    IdentityBusiness,
    IdentityEstablishment
)

from models import (
    NavigationItem,
    NavigationTypes
)


class NavigationTopView(FragmentView):
    template_name = 'navigation/nav_top.html'
    view_name = 'nav_top'

    def process_context(self):
        local_context = copy.copy(self.context)

        menu_name = local_context.get('top_menu_name')

        if menu_name:
            local_context.update({
                'navigation_items': NavigationItem.objects.filter(
                    menu_name=menu_name
                )
            })

        return local_context


class NavigationSideView(FragmentView):
    template_name = 'navigation/nav_side.html'
    view_name = 'nav_side'

    def process_context(self):
        request = self.request
        local_context = copy.copy(self.context)

        if request:
            current_identity_id = request.session.get('current_identity_id')
            try:
                current_identity = Identity.objects.get(id=current_identity_id)

            except:
                current_identity = None

        else:
            current_identity = None

        establishments = self.context.get('establishments')

        if current_identity:
            if current_identity.identity_type == IdentityTypes.BUSINESS:
                if not establishments:
                    establishments = (
                        IdentityEstablishment.objects.get_establishments(
                            current_identity
                        )
                    )
                    local_context['establishments'] = establishments

        local_context['NAVIGATION_TYPES'] = NavigationTypes
        default_navigation = NavigationItem.objects.filter_ordered(
            menu_name='default'
        )

        if (
            current_identity and
            IdentityTypes.BUSINESS == current_identity.identity_type
        ):
            merchant_navigation = NavigationItem.objects.filter_ordered(
                menu_name='merchant'
            )

        else:
            merchant_navigation = []

        local_context['navigation_items'] = list(
            chain(
                default_navigation,
                merchant_navigation
            )
        )

        return local_context

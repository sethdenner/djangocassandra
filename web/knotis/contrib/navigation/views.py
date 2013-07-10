from django.views.generic import View

from knotis.views.mixins import RenderTemplateFragmentMixin

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


class NavigationTopView(View, RenderTemplateFragmentMixin):
    template_name = 'navigation/nav_top.html'
    view_name = 'nav_top'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        context['navigation_items'] = NavigationItem.objects.filter(
            menu_name='nav_top'
        )

        return super(
            NavigationTopView,
            cls
        ).render_template_fragment(context)


class NavigationSideView(View, RenderTemplateFragmentMixin):
    template_name = 'navigation/nav_side.html'
    view_name = 'nav_side'

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        context['NAVIGATION_TYPES'] = NavigationTypes
        context['navigation_items'] = NavigationItem.objects.filter_ordered(
            menu_name='default'
        )

        request = context.get('request')
        if request:
            current_identity_id = request.session.get('current_identity_id')
            try:
                current_identity = Identity.objects.get(id=current_identity_id)

            except:
                current_identity = None

        else:
            current_identity = None

        businesses = context.get('businesses')
        establishments = context.get('establishments')

        if current_identity:
            if current_identity.identity_type == IdentityTypes.INDIVIDUAL:
                if not businesses:
                    businesses = IdentityBusiness.objects.get_businesses(
                        current_identity
                    )
                    context['businesses'] = businesses

            if current_identity.identity_type != IdentityTypes.ESTABLISHMENT:
                if not establishments:
                    establishments = (
                        IdentityEstablishment.objects.get_establishments(
                            current_identity
                        )
                    )
                    context['establishments'] = establishments

        return super(
            NavigationSideView,
            cls
        ).render_template_fragment(context)

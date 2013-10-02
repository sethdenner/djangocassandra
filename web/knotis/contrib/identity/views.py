import copy

from django import http
from django.conf import settings
from django.template import Context
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import (
    render,
    get_object_or_404
)
from django.utils import log
logger = log.getLogger(__name__)

from knotis.views import (
    ContextView,
    FragmentView
)

from knotis.contrib.auth.models import UserInformation
from knotis.contrib.maps.forms import GeocompleteForm
from knotis.contrib.media.models import Image
from knotis.contrib.offer.models import OfferAvailability
from knotis.contrib.offer.views import (
    OfferTile,
    OfferCreateTile
)

from knotis.contrib.layout.views import GridSmallView
from models import (
    IdentityTypes,
    Identity,
    IdentityIndividual,
    IdentityEstablishment
)

from forms import (
    IdentityIndividualSimpleForm,
    IdentityBusinessSimpleForm
)


class IdentityView(ContextView):
    template_name = 'knotis/identity/identity_view.html'

    def process_context(self):
        return self.context


class BusinessesView(ContextView):
    template_name = 'knotis/identity/businesses_view.html'

    def process_context(self):
        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'knotis/identity/css/profile.css',
            'styles/default/fileuploader.css'
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js'
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
        })
        return local_context


class BusinessesGrid(GridSmallView):
    view_name = 'businesses_grid'

    def process_context(self):
        establishments = IdentityEstablishment.objects.all()

        tiles = []

        if establishments:
            for establishment in establishments:
                establishment_tile = IdentityTile()
                establishment_context = Context({
                    'identity': establishment
                })
                tiles.append(
                    establishment_tile.render_template_fragment(
                        establishment_context
                    )
                )

        local_context = copy.copy(self.context)
        local_context.update({'tiles': tiles})

        return local_context


class IdentityTile(FragmentView):
    template_name = 'knotis/identity/tile.html'
    view_name = 'identity_tile'


class EstablishmentProfileGrid(GridSmallView):
    view_name = 'establishment_profile_grid'

    def process_context(self):
        establishment_offers = self.context.get('establishment_offers')

        tiles = []

        is_manager = self.context.get('is_manager')
        if is_manager:
            offer_create_tile = OfferCreateTile()
            tiles.append(
                offer_create_tile.render_template_fragment(Context({
                    'create_type': 'Promotion',
                    'create_action': '/offer/create/',
                    'action_type': 'modal'
                }))
            )

        if establishment_offers:
            for offer in establishment_offers:
                offer_tile = OfferTile()
                offer_context = Context({
                    'offer': offer
                })
                tiles.append(
                    offer_tile.render_template_fragment(offer_context)
                )

        local_context = copy.copy(self.context)
        local_context.update({'tiles': tiles})

        return local_context


class EstablishmentProfileView(ContextView):
    template_name = 'knotis/identity/profile_establishment.html'
    view_name = 'establishment_profile'

    def process_context(self):
        request = self.request
        establishment_id = self.kwargs.get('establishment_id')
        backend_name = self.kwargs.get('backend_name')

        try:
            if establishment_id:
                establishment = get_object_or_404(
                    IdentityEstablishment,
                    pk=establishment_id
                )

            elif backend_name:
                establishment = get_object_or_404(
                    IdentityEstablishment,
                    backend_name=backend_name
                )

            else:
                raise IdentityEstablishment.DoesNotExist()

        except:
            raise http.Http404

        is_manager = False
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity_id')
            current_identity = Identity.objects.get(
                pk=current_identity_id
            )

            if current_identity.identity_type == IdentityTypes.BUSINESS:
                establishments_managed = (
                    IdentityEstablishment.objects.get_establishments(
                        current_identity
                    )
                )

                for managed in establishments_managed:
                    if managed.id == establishment.id:
                        is_manager = True
                        break

        styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'knotis/identity/css/profile.css',
            'styles/default/fileuploader.css'
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js'
        ]

        if establishment.badge_image:
            profile_logo = establishment.badge_image

        else:
            profile_logo = None

        if is_manager:
            default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/add_logo.png'
            ])

        else:
            default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/profile_default.png'
            ])

        try:
            establishment_offers = OfferAvailability.objects.filter(
                identity=establishment
            )

        except:
            logger.exception('failed to get establishment offers')

        local_context = copy.copy(self.context)
        local_context.update({
            'establishment': establishment,
            'is_manager': is_manager,
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'default_profile_logo_uri': default_profile_logo_uri,
            'profile_logo': profile_logo,
            'establishment_offers': establishment_offers
        })

        return local_context


class FirstIdentityView(FragmentView):
    template_name = 'knotis/identity/first.html'
    view_name = 'identity_edit'

    def process_context(self):
        request = self.request

        try:
            individual = IdentityIndividual.objects.get_individual(
                request.user
            )

        except:
            individual = None

        local_context = copy.copy(self.context)
        local_context.update({
            'individual_form': IdentityIndividualSimpleForm(
                form_id='id-individual-form',
                description_text=(
                    'First thing\'s first. Tell us '
                    'your name so we can personalize '
                    'your Knotis account.'
                ),
                help_text=(
                    'This is the name that will be displayed '
                    'publicly in Knotis services.'
                ),
                instance=individual
            ),
            'business_form': IdentityBusinessSimpleForm(
                form_id='id-business-form',
                initial={'individual_id': individual.id}
            ),
            'location_form': GeocompleteForm()
        })

        return local_context


class IdentitySwitcherView(FragmentView):
    template_name = 'knotis/identity/switcher.html'
    view_name = 'identity_switcher'

    # make login required for all methods
    @method_decorator(login_required)
    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):
        return super(IdentitySwitcherView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def _update_current_identity(
        self,
        request,
        identity_id,
        *args,
        **kwargs
    ):
        try:
            available_identities = Identity.objects.get_available(
                user=request.user
            )
            identity = None
            for i in available_identities:
                if i.id == identity_id:
                    identity = i

            if not identity:
                msg = ''.join([
                    'identity {',
                    identity_id,
                    '} is not available to user {',
                    request.user.id,
                    '}'
                ])
                logger.warning(msg)
                return http.HttpResponseServerError(msg)

            request.session['current_identity_id'] = identity.id
            return http.HttpResponseRedirect(
                request.META.get('HTTP_REFERER', '/')
            )

        except Exception, e:
            logger.exception(
                'identity with id=%s does not exist.' % identity_id
            )
            return http.HttpResponseServerError(e)

    def get(
        self,
        request,
        identity_id=None,
        *args,
        **kwargs
    ):
        if identity_id:
            return self._update_current_identity(
                request,
                identity_id,
                *args,
                **kwargs
            )

        else:
            return super(IdentitySwitcherView, self).get(
                request,
                *args,
                **kwargs
            )

    def process_context(self):
        request = self.request
        if not request:
            return ''

        if not request.user.is_authenticated():
            return ''

        local_context = copy.copy(self.context)

        key_available = 'available_identities'
        try:
            local_context[key_available] = Identity.objects.get_available(
                user=request.user
            )

        except:
            logger.exception('failed to get available identities.')

        current_identity_id = request.session.get('current_identity_id')
        if not current_identity_id:
            try:
                user_information = UserInformation.objects.get(
                    user=request.user
                )
                request.session[
                    'current_identity_id'
                ] = user_information.default_identity_id

            except:
                logger.exception('failed to get current identity')

        return local_context

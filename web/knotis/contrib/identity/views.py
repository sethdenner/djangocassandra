import copy
from django import http
from django.conf import settings
from django.template import Context
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import (
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
from knotis.contrib.media.models import ImageInstance
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

from knotis.contrib.relation.models import Relation

from forms import (
    IdentityIndividualSimpleForm,
    IdentityBusinessSimpleForm
)

from knotis.contrib.location.models import (
    Location,
    LocationItem
)

from knotis.contrib.maps.views import GoogleMap

from knotis.contrib.endpoint.models import *

from knotis.contrib.identity.models import *


EndpointTypeNames = dict((key, name) for (key, name) in EndpointTypes.CHOICES)


class IdentityView(ContextView):
    template_name = 'knotis/identity/identity_view.html'

    def process_context(self):
        context = copy.copy(self.context)

        identity_id = self.kwargs.get('id')
        if not identity_id:
            raise Exception('No Identity supplied')

        identity = Identity.objects.get(pk=identity_id)
        if not identity:
            raise Exception('Identity not found')

        if identity.identity_type == IdentityTypes.ESTABLISHMENT:
            profile_view = EstablishmentProfileView()
            context['establishment_id'] = identity_id

        elif identity.identity_type == IdentityTypes.BUSINESS:
            try:
                establishments = (
                    IdentityEstablishment.objects.get_establishments(
                        identity
                    )
                )

            except:
                establishments = None
                logger.exception('Failed to get establishments for business')

            if 1 == len(establishments):
                profile_view = EstablishmentProfileView()
                context['establishment_id'] = establishments[0].pk

            else:
                profile_view = BusinessProfileView()
                context['establishments'] = establishments

        else:
            raise Exception('IdentityType not currently supported')

        context.update({
            'profile_markup': profile_view.render_template_fragment(context)
        })

        return context


class BusinessesView(FragmentView):
    template_name = 'knotis/identity/businesses_view.html'

    def process_context(self):
        styles = self.context.get('styles', [])
        post_scripts = self.context.get('post_scripts', [])

        my_styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'knotis/identity/css/profile.css',
            'styles/default/fileuploader.css'
        ]

        for style in my_styles:
            if not style in styles:
                styles.append(style)

        my_post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js',
            'knotis/api/js/api.js',
            'knotis/identity/js/business-tile.js'
        ]

        for script in my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
        })
        return local_context


class BusinessesGrid(GridSmallView):
    view_name = 'businesses_grid'

    def process_context(self):
        businesses = IdentityBusiness.objects.all()

        tiles = []

        if businesses:
            for business in businesses:
                business_tile = IdentityTile()
                business_context = Context({
                    'identity': business,
                    'request': self.request
                })
                tiles.append(
                    business_tile.render_template_fragment(
                        business_context
                    )
                )

        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles,
            'tile_link_template': '/id/',  # + identity.id
            'request': self.request
        })

        return local_context


class IdentityTile(FragmentView):
    template_name = 'knotis/identity/tile.html'
    view_name = 'identity_tile'

    def process_context(self):
        request = self.context.get('request')
        identity = self.context.get('identity')

        following = False
        render_follow = False
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity_id')
            current_identity = Identity.objects.get(
                pk=current_identity_id
            )

            if current_identity.identity_type == IdentityTypes.INDIVIDUAL:
                render_follow = True

                follows = Relation.objects.get_following(current_identity)
                for follow in follows:
                    if (
                        (not follow.deleted) and
                        (follow.related.id == identity.id)
                    ):
                        following = True
                        break
        else:
            current_identity = None

        try:
            profile_badge_image = ImageInstance.objects.get(
                related_object_id=identity.id,
                context='profile_badge',
                primary=True
            )

        except:
            profile_badge_image = None

        if (
            not profile_badge_image and
            identity.identity_type == IdentityTypes.ESTABLISHMENT
        ):
            try:
                business = IdentityBusiness.objects.get_establishment_parent(
                    identity
                )
                profile_badge_image = ImageInstance.objects.get(
                    related_object_id=business.pk,
                    context='profile_badge',
                    primary=True
                )

            except:
                pass

        try:
            profile_banner_image = ImageInstance.objects.get(
                related_object_id=identity.id,
                context='profile_banner',
                primary=True
            )

        except:
            profile_banner_image = None

        if (
            not profile_banner_image and
            identity.identity_type == IdentityTypes.ESTABLISHMENT
        ):
            try:
                business = IdentityBusiness.objects.get_establishment_parent(
                    identity
                )
                profile_banner_image = ImageInstance.objects.get(
                    related_object_id=business.pk,
                    context='profile_banner',
                    primary=True
                )

            except:
                pass

        local_context = copy.copy(self.context)
        local_context.update({
            'current_identity': current_identity,
            'render_follow': render_follow,
            'following': following,
            'banner_image': profile_banner_image,
            'badge_image': profile_badge_image,
            'STATIC_URL': settings.STATIC_URL
        })

        return local_context


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
                    'offer': offer.offer
                })
                tiles.append(
                    offer_tile.render_template_fragment(offer_context)
                )

        local_context = copy.copy(self.context)
        local_context.update({'tiles': tiles})

        return local_context

get_class = lambda x: globals()[x]


class BusinessProfileView(FragmentView):
    template_name = 'knotis/identity/profile_business.html'
    view_name = 'business_profile'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        pass

    def process_context(self):
        pass


class EstablishmentProfileView(FragmentView):
    template_name = 'knotis/identity/profile_establishment.html'
    view_name = 'establishment_profile'

    def process_context(self):
        request = self.request
        establishment_id = self.context.get('establishment_id')
        backend_name = self.context.get('backend_name')

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
            logger.exception(
                'failed to get establishment with id ' + establishment_id
            )
            raise http.Http404

        try:
            business = IdentityBusiness.objects.get_establishment_parent(
                establishment
            )

        except:
            logger.exception(
                ' '.join([
                    'failed to get business for establishment with id ',
                    establishment_id
                ])
            )
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
            'styles/default/fileuploader.css',
            'knotis/identity/css/first.css'
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
            'knotis/identity/js/profile.js',
            'geocomplete/jquery.geocomplete.min.js',
            'knotis/layout/js/forms.js',
            'knotis/maps/js/maps.js',
            'knotis/identity/js/update_profile.js',
        ]

        profile_badge_image = None

        # if there is no profile badge on establishment check business
        if not profile_badge_image:
            try:
                profile_badge_image = ImageInstance.objects.get(
                    related_object_id=business.pk,
                    context='profile_badge',
                    primary=True
                )

            except:
                pass

        try:
            profile_banner_image = ImageInstance.objects.get(
                related_object_id=business.pk,
                context='profile_banner',
                primary=True
            )
        except:
            profile_banner_image = None

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
                identity=establishment,
                available=True
            )

        except:
            logger.exception('failed to get establishment offers')

        locationItem = LocationItem.objects.filter(
            related_object_id=establishment.id
        )
        if len(locationItem):
            address = locationItem[0].location.address
        else:
            address = None

        maps = GoogleMap(settings.GOOGLE_MAPS_API_KEY)
        maps_scripts = maps.render_api_js()

        endpoints = []
        for endpoint_class in (EndpointPhone, EndpointEmail, EndpointFacebook, EndpointYelp, EndpointTwitter, EndpointWebsite):

            endpoint = endpoint_class.objects.get_primary_endpoint(
                identity=establishment,
                endpoint_type=endpoint_class.EndpointType
            )

            endpoint_type_name = EndpointTypeNames[endpoint_class.EndpointType]
            endpoint_type_name = endpoint_type_name.lower()

            if endpoint:
                display = None
                if endpoint.endpoint_type == EndpointTypes.YELP:
                    display = 'Yelp'
                elif endpoint.endpoint_type == EndpointTypes.FACEBOOK:
                    display = 'Facebook'

                fake_endpoint = {
                    'id': endpoint.id,
                    'endpoint_type_name': endpoint_type_name,
                    'value': endpoint.value,
                    'uri': endpoint.get_uri(),
                    'display': display
                }

                endpoints.append(fake_endpoint)

            else:
                endpoints.append({
                    'endpoint_type_name': endpoint_type_name,
                    'value': None
                })

        profile_banner_colors = [
            'blue',
            'darkblue',
            'darkgrey',
            'lightgrey',
            'orange',
            'pink',
            'purple',
            'red',
            'turquoise',
            'yellow'
        ]
        profile_banner_color_index = int(establishment.pk[24:], 16) % 10
        profile_banner_color = profile_banner_colors[
            profile_banner_color_index
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'establishment': establishment,
            'business': business,
            'is_manager': is_manager,
            'styles': styles,
            'pre_scripts': pre_scripts,
            'post_scripts': post_scripts,
            'default_profile_logo_uri': default_profile_logo_uri,
            'address': address,
            'maps_scripts': maps_scripts,
            'profile_badge': profile_badge_image,
            'profile_banner': profile_banner_image,
            'establishment_offers': establishment_offers,
            'endpoints': endpoints,
            'profile_banner_color': profile_banner_color
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
            available_identities = Identity.objects.get_available(
                user=request.user
            )

        except:
            logger.exception('failed to get available identities.')
            raise

        for i in available_identities:
            try:
                badge_image = ImageInstance.objects.get(
                    related_object_id=i.pk,
                    context='profile_badge',
                    primary=True
                )
                i.badge_image = badge_image

            except ImageInstance.DoesNotExist:
                continue

        local_context[key_available] = available_identities

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

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

from knotis.contrib.layout.views import (
    GridSmallView,
    ActionButton,
    ButtonAction
)

from models import (
    IdentityTypes,
    Identity,
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)

from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)

from forms import (
    IdentityIndividualSimpleForm,
    IdentityBusinessSimpleForm
)

from knotis.contrib.location.models import (
    LocationItem
)

from knotis.contrib.maps.views import GoogleMap

from knotis.contrib.twitter.views import get_twitter_feed_json
from knotis.contrib.yelp.views import get_reviews_by_yelp_id
import json

from knotis.views import AJAXFragmentView

from knotis.contrib.endpoint.models import (
    EndpointTypes,
    EndpointTypeNames,
    Endpoint,
    EndpointPhone,
    EndpointEmail,
    EndpointFacebook,
    EndpointYelp,
    EndpointTwitter,
    EndpointWebsite
)


class IdentityView(ContextView):
    template_name = 'knotis/identity/identity_view.html'

    def process_context(self):
        self.context = copy.copy(self.context)

        identity_id = self.kwargs.get('id')
        if not identity_id:
            raise Exception('No Identity supplied')

        identity = Identity.objects.get(pk=identity_id)
        if not identity:
            raise Exception('Identity not found')

        if identity.identity_type == IdentityTypes.ESTABLISHMENT:
            profile_view = EstablishmentProfileView()
            self.context['establishment_id'] = identity_id
            self.context['establishment'] = identity

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
                self.context['establishment_id'] = establishments[0].pk
                self.context['establishment'] = establishments[0]

            else:
                profile_view = BusinessProfileView()
                self.context['establishments'] = establishments

        else:
            raise Exception('IdentityType not currently supported')

        self.context.update({
            'profile_markup': profile_view.render_template_fragment(
                self.context
            )
        })

        return self.context


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
            'knotis/layout/js/action_button.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js',
            'knotis/api/js/api.js',
            'knotis/identity/js/business-tile.js',
            'knotis/identity/js/businesses.js'
        ]

        for script in my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)

        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'fixed_side_nav': True
        })
        return local_context


class BusinessesGrid(GridSmallView):
    view_name = 'businesses_grid'

    def process_context(self):
        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count
        businesses = IdentityBusiness.objects.all()[start_range:end_range]

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


class IdentityTileActionButton(ActionButton):
    view_name = 'identity_tile_action'

    def actions(self):
        identity = self.context.get('identity')
        current_identity = self.context.get('current_identity')

        if not current_identity:
            return None

        return [
            ButtonAction(
                'Follow',
                '/api/v1/relation/', {
                    'relation-type': RelationTypes.FOLLOWING,
                    'subject': current_identity.pk,
                    'related': identity.pk
                },
                'get'
            )
        ]


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

        profile_banner_colors = [
            'blue',
            'darkblue',
            'turquoise',
        ]
        profile_banner_color_index = int(identity.pk[24:], 16) % 3
        profile_banner_color = profile_banner_colors[
            profile_banner_color_index
        ]

        local_context = copy.copy(self.context)
        local_context.update({
            'current_identity': current_identity,
            'render_follow': render_follow,
            'following': following,
            'banner_image': profile_banner_image,
            'badge_image': profile_badge_image,
            'STATIC_URL': settings.STATIC_URL,
            'profile_banner_color': profile_banner_color
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


class EstablishmentProfileOffers(FragmentView):
    template_name = 'knotis/identity/establishment_offers.html'
    view_name = 'establishment_offers'

    def process_context(self):
        local_context = copy.copy(self.context)
        return local_context


class EstablishmentProfileLocation(FragmentView):
    template_name = 'knotis/identity/establishment_about_location.html'
    view_name = 'establishment_location'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')

        locationItem = LocationItem.objects.filter(
            related_object_id=establishment_id
        )
        if len(locationItem):
            address = locationItem[0].location.address
            latitude = locationItem[0].location.latitude
            longitude = locationItem[0].location.longitude
        else:
            address = None
            latitude = None,
            longitude = None

        local_context = copy.copy(self.context)
        local_context.update({
            'address': address,
            'latitude': latitude,
            'longitude': longitude
        })
        return local_context


class EstablishmentAboutAbout(AJAXFragmentView):
    template_name = 'knotis/identity/establishment_about_about.html'
    view_name = 'establishment_about_about'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')

        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        business = IdentityBusiness.objects.get_establishment_parent(
            establishment
        )

        local_context = copy.copy(self.context)
        local_context.update({
            'description': business.description
        })

        # Fetch and add the address and coordinates to local_context
        locationItem = LocationItem.objects.filter(
            related_object_id=business.pk
        )
        if len(locationItem):
            address = locationItem[0].location.address
            address_latitude = locationItem[0].location.latitude,
            address_longitude = locationItem[0].location.longitude
        else:
            address = None
            address_latitude = None
            address_longitude = None

        local_context.update({
            'address': address,
            'address_latitude': address_latitude,
            'address_longitude': address_longitude
        })

        # add business name to local_context
        local_context.update({
            'business': business
        })

        # add contact info (endpoints) to local_context
        endpoints = self.context.get('endpoints')
        for endpoint in endpoints:

            local_context.update({
                endpoint['endpoint_type_name']: {
                    'value': endpoint['value'],
                    'id': endpoint['id'],
                    'endpoint_type': endpoint['endpoint_type'],
                    'display': endpoint['display'],
                    'uri': endpoint['uri']
                }
            })

        # return local_context
        return local_context

    def post(
            self,
            request,
            *args,
            **kwargs
    ):

        data = json.loads(request.POST.get('data'))
        business_id = data['business_id']
        business = IdentityBusiness.objects.get(pk=business_id)

        # business name
        response = {}
        response['business_id'] = business_id
        if 'changed_name' in data:
            business.name = data['changed_name']
            business.save()

        if 'changed_description' in data:
            business.description = data['changed_description']
            business.save()

        # endpoints
        def endpoint_to_dict(endpoint):
            sendable = {
                'pk': endpoint.pk,
                'endpoint_type': endpoint.endpoint_type,
                'value': endpoint.value,
                'url': endpoint.get_uri()
            }

            return sendable

        updated_endpoints = []
        deleted_endpoints = []
        if 'changed_endpoints' in data:
            for endpoint_name in data['changed_endpoints'].keys():
                endpoint = data['changed_endpoints'][endpoint_name]
                endpoint_id = endpoint['endpoint_id']

                endpoint_value = endpoint['endpoint_value'].strip()
                    
                updated_endpoint = Endpoint.objects.update_or_create(
                    identity=business,
                    pk=endpoint_id,
                    endpoint_type=int(endpoint['endpoint_type']),
                    value=endpoint_value,
                    primary=True
                )
                
                if updated_endpoint.deleted:
                    deleted_endpoints.append(updated_endpoint)
                else:
                    updated_endpoints.append(updated_endpoint)

        return self.generate_response({
            'status': 'ok',
            'updated_endpoints': map(endpoint_to_dict, updated_endpoints),
            'deleted_endpoints': map(endpoint_to_dict, deleted_endpoints)
        })


class EstablishmentAboutTwitterFeed(FragmentView):
    template_name = 'knotis/identity/establishment_about_twitter.html'
    view_name = 'establishment_about_twitter'

    def process_context(self):
        local_context = copy.copy(self.context)

        endpoints = self.context.get('endpoints')
        twitter_endpoint = None
        for endpoint in endpoints:
            if endpoint['endpoint_type_name'] == 'twitter':
                if endpoint['value']:
                    twitter_endpoint = endpoint
                    local_context.update({
                        'twitter_handle': twitter_endpoint['value'],
                    })

        twitter_feed = None
        if(twitter_endpoint):
            feed_json = get_twitter_feed_json(twitter_endpoint['value'])
            if feed_json:
                twitter_feed = json.loads(feed_json)
                local_context.update({
                    'twitter_feed': twitter_feed
                })

        return local_context


class EstablishmentAboutYelpFeed(FragmentView):
    template_name = 'knotis/identity/establishment_about_yelp.html'
    view_name = 'establishment_about_yelp'

    def process_context(self):
        endpoints = self.context.get('endpoints')
        yelp_endpoint = None

        for endpoint in endpoints:
            if endpoint['endpoint_type_name'] == 'yelp':
                if endpoint['value']:
                    yelp_endpoint = endpoint

        yelp_feed = None
        if yelp_endpoint:
            yelp_feed = get_reviews_by_yelp_id(yelp_endpoint['value'])

        local_context = copy.copy(self.context)
        local_context.update({
            'yelp_feed': yelp_feed
        })

        return local_context


class EstablishmentAboutCarousel(FragmentView):
    template_name = 'knotis/identity/establishment_about_carousel.html'
    view_name = 'establishment_about_carousel'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')

        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        business = IdentityBusiness.objects.get_establishment_parent(
            establishment
        )

        images = ImageInstance.objects.filter(
            related_object_id=business.pk,
            context='business_profile_carousel'
        )

        image_infos = []
        count = 0
        for image in images:
            image_infos.append((count, image))
            count += 1

        local_context = copy.copy(self.context)
        local_context.update({
            'images': image_infos,
            'establishment_parent': business
        })

        return local_context


class EstablishmentProfileAbout(FragmentView):
    template_name = 'knotis/identity/establishment_about.html'
    view_name = 'establishment_about'

    def process_context(self):
        local_context = copy.copy(self.context)
        sections = []
        
        about_markup = EstablishmentAboutAbout().render_template_fragment(
            local_context
        ).strip()
        if about_markup:
            sections.append(about_markup)
            
        yelp_markup = EstablishmentAboutYelpFeed().render_template_fragment(
            local_context
        ).strip()
        if yelp_markup:
            sections.append(yelp_markup)
        
        twitter_markup = EstablishmentAboutTwitterFeed().render_template_fragment(
            local_context
        ).strip()
        if twitter_markup:
            sections.append(twitter_markup)

        carousel_markup = EstablishmentAboutCarousel().render_template_fragment(
            local_context
        ).strip()
        if carousel_markup:
            sections.append(carousel_markup)

        location_markup = EstablishmentProfileLocation().render_template_fragment(
            local_context
        ).strip()
        if location_markup:
            sections.append(location_markup)

        local_context.update({
            'sections': sections
        })
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
            'geocomplete/jquery.geocomplete.min.js',
            'knotis/layout/js/forms.js',
            'knotis/maps/js/maps.js',
            'knotis/identity/js/establishment_about.js',
            'knotis/identity/js/update_profile.js',
            'knotis/identity/js/profile.js'
        ]

        request = self.request
        establishment_id = self.context.get('establishment_id')
        establishment = self.context.get('establishment')
        backend_name = self.context.get('backend_name')

        if not establishment:
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

            is_manager = current_identity.is_manager(establishment)

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

        # if there is no profile badge on establishment check business
        profile_badge_image = None
        try:
            profile_badge_image = ImageInstance.objects.get(
                related_object_id=establishment_id,
                context='profile_badge',
                primary=True
            )

        except ImageInstance.DoesNotExist:
            try:
                if not profile_badge_image:
                    profile_badge_image = ImageInstance.objects.get(
                        related_object_id=business.pk,
                        context='profile_badge',
                        primary=True
                    )
            except Exception as err:
                logger.exception(err)

        except Exception as err:
            logger.exception(err)

        # if there is no profile banner on establishment check business
        profile_banner_image = None
        try:
            profile_banner_image = ImageInstance.objects.get(
                related_object_id=establishment_id,
                context='profile_banner',
                primary=True
            )

        except ImageInstance.DoesNotExist:
            try:
                profile_banner_image = ImageInstance.objects.get(
                    related_object_id=business.pk,
                    context='profile_banner',
                    primary=True
                )

            except Exception as err:
                logger.exception(err)

        except Exception as err:
            logger.exception(err)

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

        endpoints = Endpoint.objects.filter(identity=business, primary=True)
        endpoints = endpoints.select_subclasses()

        endpoint_dicts = []
        for endpoint_class in (
                EndpointPhone,
                EndpointEmail,
                EndpointFacebook,
                EndpointYelp,
                EndpointTwitter,
                EndpointWebsite
        ):

            endpoint = None
            for ep in endpoints:
                if ep.endpoint_type == endpoint_class.EndpointType:
                    endpoint = ep

            endpoint_type_name = EndpointTypeNames[endpoint_class.EndpointType]
            endpoint_type_name = endpoint_type_name.lower()

            if endpoint and endpoint.value:

                display = None
                if endpoint.endpoint_type == EndpointTypes.YELP:
                    display = 'Yelp'
                elif endpoint.endpoint_type == EndpointTypes.FACEBOOK:
                    display = 'Facebook'

                endpoint_dict = {
                    'id': endpoint.id,
                    'endpoint_type_name': endpoint_type_name,
                    'value': endpoint.value,
                    'uri': endpoint.get_uri(),
                    'display': display,
                    'endpoint_type': endpoint_class.EndpointType
                }

                endpoint_dicts.append(endpoint_dict)

            else:
                endpoint_dicts.append({
                    'id': '',
                    'endpoint_type_name': endpoint_type_name,
                    'value': '',
                    'uri': '',
                    'display': '',
                    'endpoint_type': endpoint_class.EndpointType
                })

        # endpoints displayed on the cover
        phone = None
        website = None
        for endpoint in endpoints:
            if EndpointTypes.PHONE == endpoint.endpoint_type:
                phone = {
                    'value': endpoint.value,
                    'uri': endpoint.get_uri()
                }

            if EndpointTypes.WEBSITE == endpoint.endpoint_type:
                website = {
                    'value': endpoint.value,
                    'uri': endpoint.get_uri()
                }

            if phone and website:
                break

        # determine nav view
        context_context = Context({
            'request': request,
            'establishment_id': establishment_id,
            'endpoints': endpoint_dicts,
            'is_manager': is_manager
        })

        if establishment_offers:
            default_view_name = 'offers'

        else:
            default_view_name = 'about'

        view_name = self.context.get('view_name', None)
        if not view_name:
            view_name = default_view_name

        if view_name == 'contact':
            profile_content = (
                EstablishmentProfileLocation().render_template_fragment(
                    context_context
                )
            )
            content_plexer = 'offersaboutcontact'

        elif view_name == 'offers':
            content_plexer = 'offersaboutcontact'
            profile_content = None

        elif view_name == 'about':
            content_plexer = 'offersaboutcontact'
            profile_content = (
                EstablishmentProfileAbout().render_template_fragment(
                    context_context
                )
            )

        else:
            content_plexer = 'establishments'
            profile_content = 'establishments'

        profile_banner_colors = [
            'blue',
            'darkblue',
            'turquoise'
        ]
        profile_banner_color_index = int(business.pk[24:], 16) % 3
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
            'phone': phone,
            'website': website,
            'maps_scripts': maps_scripts,
            'profile_badge': profile_badge_image,
            'profile_banner': profile_banner_image,
            'establishment_offers': establishment_offers,
            'top_menu_name': 'identity_profile',
            'profile_content': profile_content,
            'content_plexer': content_plexer,
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
        local_context['IdentityTypes'] = IdentityTypes

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

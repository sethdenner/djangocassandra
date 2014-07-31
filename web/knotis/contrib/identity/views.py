import copy
from django import http
from django.conf import settings
from django.template import Context
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import log
from knotis.utils.regex import REGEX_UUID
logger = log.getLogger(__name__)

from knotis.views import (
    EmbeddedView,
    ModalView,
    FragmentView
)


from knotis.contrib.auth.models import UserInformation
from knotis.contrib.media.models import (
    ImageInstance
)

from knotis.contrib.layout.views import (
    GridSmallView,
    ActionButton,
    ButtonAction,
    DefaultBaseView
)

from models import (
    IdentityTypes,
    Identity,
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment
)


from knotis.contrib.relation.models import (
    RelationTypes,
    Relation,
)

from forms import (
    IdentityForm
)

from knotis.contrib.location.models import (
    LocationItem
)


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
    EndpointWebsite,
    EndpointIdentity
)

from .mixins import GetCurrentIdentityMixin
from .api import IdentityApi


def get_current_identity(request):
    current_identity_id = request.session['current_identity']
    try:
        current_identity = Identity.objects.get(pk=current_identity_id)
        return current_identity

    except:
        logger.exception('Failed to get current identity')
        return None


def get_identity_image(identity, context):
    try:
        image = ImageInstance.objects.get(
            related_object_id=identity.id,
            context=context,
            primary=True
        )

    except ImageInstance.DoesNotExist:
        image = None

    except Exception, e:
        logger.exception(e.message)
        return None

    if (
        not image and
        identity.identity_type == IdentityTypes.ESTABLISHMENT
    ):
        try:
            business = IdentityBusiness.objects.get_establishment_parent(
                identity
            )
            image = ImageInstance.objects.get(
                related_object_id=business.pk,
                context=context,
                primary=True
            )

        except ImageInstance.DoesNotExist:
            pass

        except Exception, e:
            logger.exception(e.message)

    return image


def get_identity_profile_badge(identity):
    return get_identity_image(
        identity,
        'profile_badge'
    )


def get_identity_profile_banner(identity):
    return get_identity_image(
        identity,
        'profile_banner'
    )


def get_identity_default_profile_banner_color(identity):
    profile_banner_colors = [
        'blue',
        'darkblue',
        'turquoise'
    ]
    profile_banner_color_index = int(identity.pk[24:], 16) % 3
    profile_banner_color = profile_banner_colors[
        profile_banner_color_index
    ]

    return profile_banner_color


class EstablishmentsView(EmbeddedView):
    view_name = 'establishments'
    url_patterns = [r'^businesses/$']
    template_name = 'knotis/identity/establishments.html'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/layout/js/action_button.js',
        'knotis/identity/js/businesses.js',
        'knotis/identity/js/business-tile.js',
    ]


class EstablishmentProfileView(EmbeddedView):
    view_name = 'establishment_profile'
    url_patterns = [
        r''.join([
            '^id/(?P<identity_id>',
            REGEX_UUID,
            ')/$'
        ]),
        r''.join([
            '^id/(?P<identity_id>',
            REGEX_UUID,
            ')(/(?P<view_name>',
            '\w{1,50}',
            '))?/$'
        ])
    ]
    template_name = 'knotis/identity/establishment_profile.html'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'jcrop/js/jquery.Jcrop.js',
        'scripts/fileuploader.js',
        'scripts/jquery.colorbox.js',
        'scripts/jquery.sickle.js',
        'knotis/identity/js/profile.js',
        'knotis/identity/js/update_profile.js',
    ]

    def set_establishment(self):

        identity_id = self.context.get('identity_id')
        identity = Identity.objects.get(pk=identity_id)
        if not identity:
            raise Exception('Identity not found')

        if identity.identity_type == IdentityTypes.ESTABLISHMENT:
            self.establishment_id = identity_id
            self.establishment = identity

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

            if len(establishments) > 0:
                self.establishment_id = establishments[0].pk
                self.establishment = establishments[0]

            else:
                raise Exception('Business profile not implemented yet.')

        else:
            raise Exception('Identity profile not implemented yet.')

    def is_manager(self):
        request = self.request
        self.is_manager = False
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity')
            current_identity = Identity.objects.get(
                pk=current_identity_id
            )

            self.is_manager = (
                current_identity.is_manager(self.establishment) or
                current_identity.pk == self.establishment.pk
            )

    def set_business(self):
        if not hasattr(self, 'establishment'):
            self.set_establishment()

        try:
            self.business = IdentityBusiness.objects.get_establishment_parent(
                self.establishment
            )

        except:
            logger.exception(
                ' '.join([
                    'failed to get business for establishment with id ',
                    self.establishment_id
                ])
            )
            raise http.Http404

    def set_images(self):
        if not hasattr(self, 'business'):
            self.set_establishment()

        if self.is_manager:
            self.default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/add_logo.png'
            ])

        else:
            self.default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/profile_default.png'
            ])

        self.profile_badge_image = get_identity_profile_badge(
            self.establishment
        )
        self.profile_banner_image = get_identity_profile_banner(
            self.establishment
        )
        self.profile_banner_color = get_identity_default_profile_banner_color(
            self.establishment
        )

    def process_context(self):
        self.set_establishment()
        self.set_business()

        self.is_manager()
        self.set_images()

        locationItem = LocationItem.objects.filter(
            related_object_id=self.establishment.id
        )
        if len(locationItem):
            address = locationItem[0].location.address
        else:
            address = None


        endpoints = Endpoint.objects.filter(
            identity=self.establishment,
            primary=True
        )
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

                elif endpoint.endpoint_type == EndpointTypes.ADDRESS:
                    address = endpoint.value

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
                    'uri': endpoint.get_uri(),
                    'display': endpoint.get_display()
                }

            if phone and website:
                break

        # determine nav view
        request = self.request
        context_context = Context({
            'request': request,
            'establishment_id': self.establishment_id,
            'endpoints': endpoint_dicts,
            'is_manager': self.is_manager
        })

        """
        try:
            establishment_offers = OfferAvailability.objects.filter(
                identity=self.establishment,
                available=True
            )

        except:
            logger.exception('failed to get establishment offers')

        if establishment_offers:
            default_view_name = 'offers'

        else:
        """
        default_view_name = 'about'

        view_name = self.context.get('view_name', default_view_name)

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

        local_context = copy.copy(self.context)
        local_context.update({
            'establishment': self.establishment,
            'is_manager': self.is_manager,
            'address': address,
            'phone': phone,
            'website': website,
            'business': self.business,
            'default_profile_logo_uri': self.default_profile_logo_uri,
            'profile_badge': self.profile_badge_image,
            'profile_banner': self.profile_banner_image,
            'profile_banner_color': self.profile_banner_color,
            #  'establishment_offers': establishment_offers,
            'top_menu_name': 'identity_profile',
            'profile_content': profile_content,
            'view_name': view_name,
            'content_plexer': content_plexer,
        })

        return local_context


class EstablishmentsGrid(GridSmallView):
    view_name = 'establishments_grid'

    def process_context(self):
        current_identity_id = self.request.session.get('current_identity')
        if current_identity_id:
            current_identity = Identity.objects.get(pk=current_identity_id)

        else:
            current_identity = None

        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count
        establishments = IdentityEstablishment.objects.all()
        if (
            not current_identity or
            not current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            establishments = establishments.filter(
                available=True
            )

        establishments = establishments[start_range:end_range]

        tiles = []

        if establishments:
            for establishment in establishments:

                location_items = LocationItem.objects.filter(
                    related_object_id=establishment.pk
                )
                if len(location_items) > 0:
                    address = location_items[0].location.address
                else:
                    address = ''

                establishment_tile = IdentityTile()
                establishment_context = Context({
                    'request': self.request,
                    'identity': establishment,
                    'request': self.request,
                })

                if address:
                    establishment_context.update({'address': address})

                tiles.append(
                    establishment_tile.render_template_fragment(
                        establishment_context
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
        tile_identity = self.context.get('identity')
        current_identity = self.context.get('current_identity')

        if not current_identity:
            return [
                ButtonAction(
                    'Sign Up',
                    '/signup/',
                    {},
                    'get',
                    deep=True,
                )
            ]
        following = Relation.objects.follows(current_identity, tile_identity)
        is_following = len(following) == 0
        action_text = 'Follow' if is_following  else 'Unfollow'
        return [
            ButtonAction(
                action_text,
                '/api/v0/relation/follow/',
                {
                    'relation-type': RelationTypes.FOLLOWING,
                    'subject_id': current_identity.pk,
                    'related_id': tile_identity.pk,
                },
                'post' if is_following else 'delete'
            )
        ]


class IdentityTile(FragmentView):
    template_name = 'knotis/identity/tile.html'
    view_name = 'identity_tile'

    def process_context(self):
        request = self.context.get('request')
        identity = self.context.get('identity')

        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity')
            current_identity = Identity.objects.get(
                pk=current_identity_id
            )

        else:
            current_identity = None

        profile_badge_image = get_identity_profile_badge(identity)
        profile_banner_image = get_identity_profile_banner(identity)
        profile_banner_color = get_identity_default_profile_banner_color(
            identity
        )
        identity_tile_context = Context({
            'current_identity': current_identity,
            'identity': identity
        })
        action_button = IdentityTileActionButton()
        action_button_content = action_button.render_template_fragment(
            identity_tile_context
        )

        local_context = copy.copy(self.context)
        local_context.update({
            'current_identity': current_identity,
            'banner_image': profile_banner_image,
            'badge_image': profile_badge_image,
            'action_button': action_button_content,
            'STATIC_URL': settings.STATIC_URL,
            'profile_banner_color': profile_banner_color
        })

        return local_context

"""
class EstablishmentProfileGrid(GridSmallView):
    view_name = 'establishment_profile_grid'

    def process_context(self):
        establishment_offers = self.context.get('establishment_offers')
        request = self.context.get('request')

        offer_action = None
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity')
            current_identity = Identity.objects.get(pk=current_identity_id)
            if current_identity.identity_type  == IdentityTypes.INDIVIDUAL:
                offer_action = 'buy'

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
                    'offer': offer.offer,
                    'offer_action': offer_action
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
"""


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
            latitude = None
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
        has_data = False
        establishment_id = self.context.get('establishment_id')

        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        local_context = copy.copy(self.context)
        local_context.update({
            'description': establishment.description
        })

        if establishment.description:
            has_data = True

        # Fetch and add the address and coordinates to local_context
        locationItem = LocationItem.objects.filter(
            related_object_id=establishment.pk
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
            'STATIC_URL': settings.STATIC_URL,
            'establishment': establishment
        })

        # add contact info (endpoints) to local_context
        endpoints = self.context.get('endpoints')
        for endpoint in endpoints:
            endpoint_type_name = endpoint['endpoint_type_name']
            local_context.update({
                endpoint_type_name: {
                    'value': endpoint['value'],
                    'id': endpoint['id'],
                    'endpoint_type': endpoint['endpoint_type'],
                    'display': endpoint['display'],
                    'uri': endpoint['uri']
                }
            })
            if (
                endpoint['value'] and (
                    endpoint_type_name == 'facebook'
                    or endpoint_type_name == 'yelp'
                    or endpoint_type_name == 'twitter'
                )
            ):
                has_data = True

        local_context['has_data'] = has_data

        return local_context

    def post(
            self,
            request,
            *args,
            **kwargs
    ):

        data = json.loads(request.POST.get('data'))
        establishment_id = data['establishment_id']
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        # business name
        response = {}
        response['establishment_id'] = establishment_id
        if 'changed_name' in data:
            establishment.name = data['changed_name']

        if 'changed_description' in data:
            establishment.description = data['changed_description']

        establishment.save()

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
                    identity=establishment,
                    pk=endpoint_id,
                    endpoint_type=int(endpoint['endpoint_type']),
                    value=endpoint_value,
                    primary=True
                )

                if updated_endpoint.deleted:
                    deleted_endpoints.append(updated_endpoint)
                else:
                    updated_endpoints.append(updated_endpoint)

        return self.generate_ajax_response({
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
        self.has_feed = False
        if(twitter_endpoint):
            feed_json = get_twitter_feed_json(twitter_endpoint['value'])
            if feed_json:
                twitter_feed = json.loads(feed_json)
                self.has_feed = len(twitter_feed) > 0
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
        self.has_feed = False
        if yelp_endpoint:
            yelp_feed = get_reviews_by_yelp_id(yelp_endpoint['value'])

            self.has_feed = len(yelp_feed)

        local_context = copy.copy(self.context)
        local_context.update({
            'yelp_feed': yelp_feed
        })

        return local_context


class EstablishmentAboutFeeds(FragmentView):
    template_name = 'knotis/identity/establishment_about_feeds.html'
    view_name = 'establishment_about_feeds'

    def process_context(self):
        local_context = copy.copy(self.context)

        yelp = EstablishmentAboutYelpFeed()
        twitter = EstablishmentAboutTwitterFeed()

        local_context.update({
            'yelp_markup': yelp.render_template_fragment(local_context),
            'yelp_has_feed': yelp.has_feed,

            'twitter_markup': twitter.render_template_fragment(local_context),
            'twitter_has_feed': twitter.has_feed
        })

        return local_context


class EstablishmentAboutCarousel(FragmentView):
    template_name = 'knotis/identity/establishment_about_carousel.html'
    view_name = 'establishment_about_carousel'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        images = ImageInstance.objects.filter(
            related_object_id=establishment.pk,
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
        })

        return local_context


class EstablishmentProfileAbout(FragmentView):
    template_name = 'knotis/identity/establishment_about.html'
    view_name = 'establishment_about'

    def process_context(self):
        local_context = copy.copy(self.context)
        sections = []

        about = EstablishmentAboutAbout()
        about_markup = about.render_template_fragment(local_context)
        about_markup = about_markup.strip()
        if about_markup:
            sections.append({
                'markup': about_markup,
            })

        carousel = EstablishmentAboutCarousel()
        carousel_markup = carousel.render_template_fragment(local_context)
        carousel_markup = carousel_markup.strip()
        if carousel_markup:
            sections.append({
                'markup': carousel_markup,
            })

        feeds = EstablishmentAboutFeeds()
        feeds_markup = feeds.render_template_fragment(local_context)
        feeds_markup = feeds_markup.strip()
        if feeds_markup:
            sections.append({
                'markup': feeds_markup,
            })

        location = EstablishmentProfileLocation()
        location_markup = location.render_template_fragment(local_context)
        location_markup = location_markup.strip()
        if location_markup:
            sections.append({
                'markup': location_markup,
            })

        local_context.update({
            'sections': sections,
        })
        return local_context

get_class = lambda x: globals()[x]


class BusinessProfileView(FragmentView):
    template_name = 'knotis/identity/profile_business.html'
    view_name = 'business_profile'

    def process_context(self):
        pass


class CreateBusinessView(ModalView, GetCurrentIdentityMixin):
    url_patterns = [
        r'^identity/business/create/$'
    ]
    template_name = 'knotis/identity/business_create.html'
    view_name = 'business_create'
    default_parent_view_class = DefaultBaseView
    post_scripts = [
        'knotis/identity/js/business_create.js'
    ]

    def process_context(self):
        self.context['modal_id'] = 'business-create'
        return self.context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        current_identity = self.get_current_identity(request)
        if (
            IdentityTypes.BUSINESS == current_identity.identity_type or
            IdentityTypes.ESTABLISHMENT == current_identity.identity_type
        ):
            errors['no-field'] = (
                'This type of identity cannot create businesses.'
            )

        name = request.POST.get('name')
        if not name:
            errors['fields'] = {
                'name': 'Name is required to create a business.'
            }

        if not errors:
            try:
                business, establishment = IdentityApi.create_business(
                    current_identity.pk,
                    name=name
                )

                data['business_pk'] = business.pk
                data['establishment_pk'] = establishment.pk

            except Exception, e:
                logger.exception(e.message)
                errors['exception'] = e.message

            try:
                user_information = UserInformation.objects.get(
                    user=request.user
                )
                user_information.default_identity_id = establishment.pk
                user_information.save()
                request.session['current_identity'] = establishment.pk

            except Exception, e:
                logger.exception(e.message)

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class FirstIdentityView(ModalView):
    url_patterns = [r'^identity/first/$']
    template_name = 'knotis/identity/first.html'
    view_name = 'identity_edit'
    default_parent_view_class = DefaultBaseView

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
            'identity_id': individual.pk,
            'modal_id': 'first-id'
        })

        return local_context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        data = {}
        errors = {}

        noun = 'individual'

        identity_id = request.POST.get('id')

        try:
            identity = Identity.objects.get(pk=identity_id)

        except Exception, e:
            message = ''.join([
                'Failed to get ',
                noun,
                ' to update.'
            ])
            logger.exception(message)
            errors['no-field'] = message

        if not errors:
            form = IdentityForm(
                data=request.POST,
                instance=identity
            )

            if not form.is_valid():
                for field, messages in form.errors.iteritems():
                    errors[field] = [m for m in messages]

                data['message'] = ''.join([
                    'An error occurred during ',
                    noun,
                    ' update.'
                ])

        if not errors:
            try:
                identity = form.save()

            except Exception, e:
                message = ''.join([
                    'An error occurred while updating ',
                    noun,
                    '.'
                ])
                logger.exception(message)
                errors['no-field']  = e.message

        if not errors:
            try:
                EndpointIdentity.objects.update_identity_endpoints(identity)

            except Exception, e:
                message = ''.join([
                    'An error occurred while updating ',
                    noun,
                    '.'
                ])
                logger.exception(message)
                errors['no-field']  = e.message

        if not errors:
            data['data'] = {
                noun + '_id': identity.id,
                noun + '_name': identity.name
            }

            data['message'] = ''.join([
                noun.capitalize(),
                ' updated successfully.'
            ])

        if not errors and self.response_format == self.RESPONSE_FORMATS.HTML:
            self.response_fromat = self.RESPONSE_FORMATS.REDIRECT

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class IdentitySwitcherView(EmbeddedView):
    url_patterns = [
        r''.join([
            '^identity/switcher(/(?P<identity_id>',
            REGEX_UUID,
            '))?/$'
        ])
    ]
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

            request.session['current_identity'] = identity.pk
            try:
                user_information = UserInformation.objects.get(
                    user=request.user
                )
                user_information.default_identity_id = identity.pk
                user_information.save()
            except Exception, e:
                logger.exception(e.message)

            return http.HttpResponseRedirect(
                '/'
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
            if IdentityTypes.ESTABLISHMENT == i.identity_type:
                local_context['has_business'] = True

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

        current_identity_id = request.session.get('current_identity')
        if not current_identity_id:
            try:
                user_information = UserInformation.objects.get(
                    user=request.user
                )
                request.session[
                    'current_identity'
                ] = user_information.default_identity_id

            except:
                logger.exception('failed to get current identity')

        return local_context


class TransactionTileView(FragmentView):
    template_name = 'knotis/transaction/transaction_tile.html'
    view_name = 'transaction_tile'

    def process_context(self):
        identity = self.context['identity']

        profile_badge_image = get_identity_profile_badge(identity)
        profile_banner_image = get_identity_profile_banner(identity)
        profile_banner_color = get_identity_default_profile_banner_color(
            identity
        )

        self.context.update({
            'badge_image': profile_badge_image,
            'banner_image': profile_banner_image,
            'profile_banner_color': profile_banner_color
        })

        return self.context

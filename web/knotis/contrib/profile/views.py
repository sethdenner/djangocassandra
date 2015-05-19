
import json
import copy

from django import http
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from django.template import (
    Context,
    RequestContext
)


from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView,
)

from knotis.views import (
    FragmentView,
    EmbeddedView,
    AJAXFragmentView,
)

from knotis.contrib.media.models import ImageInstance
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes,
    EndpointTypeNames,
    EndpointEmail,
    EndpointPhone,
    EndpointYelp,
    EndpointFacebook,
    EndpointTwitter,
    EndpointWebsite,
)
from knotis.contrib.relation.models import (
    Relation,
)

from knotis.contrib.offer.models import (
    OfferAvailability,
)

from knotis.contrib.offer.views import (
    OfferTile,
    DummyOfferTile,
)


from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes,
    IdentityBusiness,
    IdentityIndividual,
    IdentityEstablishment
)
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.utils.regex import REGEX_UUID
from knotis.contrib.identity.views import (
    IdentityActionButton,
    IdentityTile,
    get_identity_profile_badge,
    get_identity_profile_banner,
    get_identity_default_profile_banner_color
)


from knotis.contrib.location.models import (
    LocationItem
)

from knotis.contrib.twitter.views import get_twitter_feed_json
from knotis.contrib.yelp.views import get_reviews_by_yelp_id


class ProfileView(EmbeddedView, GetCurrentIdentityMixin):
    view_name = 'profile'
    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/profile/profile.html'
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

    def get_images(self, can_write):

        profile_badge_image = get_identity_profile_badge(
            self.profile_identity
        )

        profile_banner_image = get_identity_profile_banner(
            self.profile_identity
        )

        if can_write:
            default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/add_logo.png'
            ])

        else:
            default_profile_logo_uri = ''.join([
                settings.STATIC_URL,
                'knotis/identity/img/profile_default.png'
            ])

        profile_banner_color = get_identity_default_profile_banner_color(
            self.profile_identity
        )

        return {
            'default_profile_logo_uri': default_profile_logo_uri,
            'profile_badge': profile_badge_image,
            'profile_banner': profile_banner_image,
            'profile_banner_color': profile_banner_color,
        }

    def process_context(self):
        identity_id = self.context.get('identity_id')
        identity = Identity.objects.get(pk=identity_id)

        if not identity:
            raise Exception('Identity not found')

        profile_context = copy.copy(self.context)

        profile_class = None
        if identity.identity_type == IdentityTypes.ESTABLISHMENT:
            profile_class = EstablishmentProfileView

        elif identity.identity_type == IdentityTypes.INDIVIDUAL:
            profile_class = IndividualProfileView

        if profile_class is not None:
            profile_content = profile_class().render_template_fragment(
                profile_context
            )
            self.post_scripts = profile_class.post_scripts
            self.styles = profile_class.styles

        else:
            profile_content = '&nbsp'

        profile_context.update({
            'profile': profile_content
        })

        return profile_context


class IndividualProfileView(ProfileView):
    view_name = 'individual_profile'
    template_name = 'knotis/profile/individual.html'
    url_patterns = [
        r'^id/update_individual/',
    ]
    post_scripts = [
        'jcrop/js/jquery.Jcrop.js',
        'scripts/fileuploader.js',
        'scripts/jquery.colorbox.js',
        'scripts/jquery.sickle.js',
        'knotis/profile/js/profile.js',
    ]

    styles = [
        'knotis/profile/css/individual.css',
    ]

    def process_context(self):
        current_identity = self.get_current_identity(self.request)

        identity_id = self.context.get('identity_id')

        self.profile_identity = Identity.objects.get(pk=identity_id)
        is_owner = (
            current_identity and
            current_identity.pk == self.profile_identity.pk
        )

        local_context = copy.copy(self.context)
        tiles = []
        relations = Relation.objects.get_following(self.profile_identity)
        for relation in relations:
            relation_tile = IdentityTile()
            relation_context = Context({
                'identity': relation.related,
                'request': self.request,
            })
            tiles.append(
                relation_tile.render_template_fragment(
                    relation_context
                )
            )

        local_context.update({
            'request': self.request,
            'identity': self.profile_identity,
            'tiles': tiles,
            'is_owner': is_owner
        })

        local_context.update(self.get_images(is_owner))

        return local_context

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = self.get_current_identity(self.request)
        profile_identity_id = request.POST.get('identity_id')

        errors = {}
        data = {}

        if not (
            current_identity and current_identity.id == profile_identity_id
        ):
            msg = "You're not allowed to do that."
            errors['no-field'] = msg
            return self.render_to_response(
                data=data,
                errors=errors,
                render_template=False
            )

        try:
            individual = IdentityIndividual.objects.get(pk=profile_identity_id)

        except:
            msg = 'Failed to find this user.'
            errors['no-field'] = msg
            return self.render_to_response(
                data=data,
                errors=errors,
                render_template=False
            )

        new_name = request.POST.get('individual_name')

        individual.name = new_name
        individual.save()

        data['next'] = ''.join([
            '/id/%s/' % profile_identity_id
        ])


        if not request.is_ajax():
            self.response_format = self.RESPONSE_FORMATS.REDIRECT

        return self.render_to_response(
            data=data,
            errors=errors,
            render_template=False
        )


class EstablishmentProfileView(ProfileView, GetCurrentIdentityMixin):
    view_name = 'establishment_profile'
    template_name = 'knotis/profile/establishment.html'
    default_parent_view_class = DefaultBaseView
    styles = [
        'knotis/profile/css/establishment.css',
    ]
    post_scripts = [
        'jcrop/js/jquery.Jcrop.js',
        'knotis/layout/js/action_button.js',
        'knotis/identity/js/identity-action.js',
        'scripts/fileuploader.js',
        'scripts/jquery.colorbox.js',
        'scripts/jquery.sickle.js',
        'knotis/profile/js/profile.js',
        'knotis/profile/js/establishment.js',
        'knotis/profile/js/update_establishment.js',
        'knotis/admintools/js/admin_toggle_manager.js',
    ]

    def set_profile_identity(self):

        identity_id = self.context.get('identity_id')
        identity = Identity.objects.get(pk=identity_id)
        if not identity:
            raise Exception('Identity not found')

        if identity.identity_type == IdentityTypes.ESTABLISHMENT:
            self.establishment_id = identity_id
            self.profile_identity = identity

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
                self.profile_identity = establishments[0]

            else:
                raise Exception('Business profile not implemented yet.')

        else:
            raise Exception('Identity profile not implemented yet.')

    def is_manager(self):
        request = self.request
        self.is_manager = False
        if request.user.is_authenticated():
            current_identity = self.get_current_identity(request)

            self.is_manager = (
                current_identity.is_manager(self.profile_identity) or
                current_identity.pk == self.profile_identity.pk
            )

    def set_business(self):
        if not hasattr(self, 'establishment'):
            self.set_profile_identity()

        try:
            self.business = IdentityBusiness.objects.get_establishment_parent(
                self.profile_identity
            )

        except:
            logger.exception(
                ' '.join([
                    'failed to get business for establishment with id ',
                    self.establishment_id
                ])
            )
            raise http.Http404

    def process_context(self):
        # Super user check.
        is_superuser = False
        request = self.request
        if request.user.is_authenticated():
            current_identity = self.get_current_identity(request)

            if (
                current_identity and
                current_identity.identity_type == IdentityTypes.SUPERUSER
            ):
                is_superuser = True
        else:
            current_identity = None

        self.set_profile_identity()
        self.set_business()

        self.is_manager()

        location_item = LocationItem.objects.filter(
            related_object_id=self.profile_identity.id
        )
        if len(location_item):
            address = location_item[0].location.address
        else:
            address = None

        endpoints = Endpoint.objects.filter(
            identity=self.profile_identity,
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
            endpoint_class_type = endpoint_class.objects.__default_endpoint_type__
            for ep in endpoints:
                if ep.endpoint_type == endpoint_class_type:
                    endpoint = ep

            endpoint_type_name = EndpointTypeNames[endpoint_class_type]
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
                    'endpoint_type': endpoint_class_type
                }

                endpoint_dicts.append(endpoint_dict)

            else:
                endpoint_dicts.append({
                    'id': '',
                    'endpoint_type_name': endpoint_type_name,
                    'value': '',
                    'uri': '',
                    'display': '',
                    'endpoint_type': endpoint_class_type
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
        content_context = RequestContext(request, {
            'request': request,
            'establishment_id': self.establishment_id,
            'endpoints': endpoint_dicts,
            'is_manager': self.is_manager
        })

        default_view_name = 'about'

        view_name = self.context.get('view_name', default_view_name)

        if view_name == 'contact':
            profile_content = (
                EstablishmentProfileLocation().render_template_fragment(
                    content_context
                )
            )
            content_plexer = 'offersaboutcontact'

        elif view_name == 'offers':
            content_plexer = 'offersaboutcontact'
            content_context[
                'offer_availability_identity'] = self.profile_identity
            profile_content = (
                OfferAvailabilityGridView().render_template_fragment(
                    content_context
                )
            )

        elif view_name == 'about':
            content_plexer = 'offersaboutcontact'
            profile_content = (
                EstablishmentProfileAbout(
                    RequestContext(request)
                ).render_template_fragment(
                    content_context
                )
            )

        else:
            content_plexer = 'establishments'
            profile_content = 'establishments'

        action_context = RequestContext(request, {
            'current_identity': current_identity,
            'identity': self.profile_identity
        })

        if ((current_identity and
                current_identity.identity_type == IdentityTypes.INDIVIDUAL) or
                current_identity is None):
            action_button = IdentityActionButton()
            action_button_content = action_button.render_template_fragment(
                action_context
            )
        else:
            action_button_content = None

        local_context = copy.copy(self.context)
        local_context.update(self.get_images(self.is_manager))
        local_context.update({
            'request': request,
            'establishment': self.profile_identity,
            'is_manager': self.is_manager,
            'address': address,
            'phone': phone,
            'website': website,
            'business': self.business,
            'top_menu_name': 'identity_profile',
            'profile_content': profile_content,
            'view_name': view_name,
            'content_plexer': content_plexer,
            'action_button': action_button_content,
            'is_superuser': is_superuser,
        })

        return local_context


class EstablishmentProfileLocation(FragmentView):
    template_name = 'knotis/profile/establishment_about_location.html'
    view_name = 'establishment_location'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')
        endpoints = self.context.get('endpoints')

        local_context = copy.copy(self.context)
        phone = website = None
        for endpoint in endpoints:
            if (
                endpoint['endpoint_type'] == EndpointTypes.PHONE and
                endpoint['value']
            ):
                phone = endpoint

            elif (
                endpoint['endpoint_type'] == EndpointTypes.WEBSITE and
                endpoint['value']
            ):
                website = endpoint

        location_item = LocationItem.objects.filter(
            related_object_id=establishment_id
        )
        if len(location_item):
            address = location_item[0].location.address
            latitude = location_item[0].location.latitude
            longitude = location_item[0].location.longitude
        else:
            address = None
            latitude = None
            longitude = None

        local_context.update({
            'address': address,
            'phone': phone,
            'website': website,
            'latitude': latitude,
            'longitude': longitude
        })
        return local_context


class EstablishmentAboutDetails(AJAXFragmentView):
    template_name = 'knotis/profile/establishment_about_details.html'
    view_name = 'establishment_about_details'

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
        location_item = LocationItem.objects.filter(
            related_object_id=establishment.pk
        )
        if len(location_item):
            address = location_item[0].location.address
            address_latitude = location_item[0].location.latitude,
            address_longitude = location_item[0].location.longitude
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
    template_name = 'knotis/profile/establishment_about_twitter.html'
    view_name = 'establishment_about_twitter'

    def process_context(self):
        local_context = copy.copy(self.context)

        endpoints = self.context.get('endpoints')
        self.endpoint = None
        for endpoint in endpoints:
            if endpoint['endpoint_type_name'] == 'twitter':
                if endpoint['value']:
                    self.endpoint = endpoint
                    local_context.update({
                        'twitter_handle': self.endpoint['value'],
                        'twitter': self.endpoint,
                    })

        twitter_feed = None
        self.has_feed = False
        if(self.endpoint):
            feed_json = get_twitter_feed_json(self.endpoint['value'])
            if feed_json:
                twitter_feed = json.loads(feed_json)
                self.has_feed = len(twitter_feed) > 0
                local_context.update({
                    'twitter_feed': twitter_feed
                })

        return local_context


class EstablishmentAboutYelpFeed(FragmentView):
    template_name = 'knotis/profile/establishment_about_yelp.html'
    view_name = 'establishment_about_yelp'

    def process_context(self):
        endpoints = self.context.get('endpoints')
        self.endpoint = None

        for endpoint in endpoints:
            if endpoint['endpoint_type_name'] == 'yelp':
                if endpoint['value']:
                    self.endpoint = endpoint

        yelp_feed = None
        self.has_feed = False
        if self.endpoint:
            yelp_feed = get_reviews_by_yelp_id(self.endpoint['value'])

            self.has_feed = len(yelp_feed)

        local_context = copy.copy(self.context)
        local_context.update({
            'yelp_feed': yelp_feed,
            'yelp': self.endpoint
        })

        return local_context


class EstablishmentAboutFeeds(FragmentView):
    template_name = 'knotis/profile/establishment_about_feeds.html'
    view_name = 'establishment_about_feeds'

    def process_context(self):
        local_context = copy.copy(self.context)

        yelp = EstablishmentAboutYelpFeed()
        twitter = EstablishmentAboutTwitterFeed()

        local_context.update({
            'yelp_markup': yelp.render_template_fragment(local_context),
            'yelp_has_feed': yelp.has_feed,
            'yelp': yelp.endpoint,

            'twitter_markup': twitter.render_template_fragment(local_context),
            'twitter_has_feed': twitter.has_feed,
            'twitter': twitter.endpoint,

            'facebook': filter(
                lambda x: x[
                    'endpoint_type_name'
                ] == 'facebook', self.context.get("endpoints"))[0],
        })

        return local_context


class EstablishmentAboutCarousel(FragmentView):
    template_name = 'knotis/profile/establishment_about_carousel.html'
    view_name = 'establishment_about_carousel'

    def process_context(self):
        establishment_id = self.context.get('establishment_id')
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)

        images = ImageInstance.objects.filter(
            related_object_id=establishment.pk,
            context='business_profile_carousel'
        )

        image_infos = []
        for count, image in enumerate(images):
            image_infos.append((count, image))

        local_context = copy.copy(self.context)
        local_context.update({
            'images': image_infos,
        })

        return local_context


class EstablishmentProfileAbout(FragmentView):
    template_name = 'knotis/profile/establishment_about.html'
    view_name = 'establishment_about'

    def process_context(self):
        local_context = copy.copy(self.context)
        sections = []

        request = self.request
        about = EstablishmentAboutDetails(
            RequestContext(request)
        )
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


class OfferAvailabilityGridView(GridSmallView):
    view_name = 'offer_availability_grid'

    def process_context(self):
        request = self.context.get('request')
        current_identity = None
        if request and request.user.is_authenticated():
            current_identity_id = request.session['current_identity']
            try:
                current_identity = Identity.objects.get(pk=current_identity_id)

            except:
                pass

        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count

        if (
            current_identity and
            current_identity.identity_type == IdentityTypes.INDIVIDUAL
        ):
            offer_action = 'buy'

        else:
            offer_action = None

        try:
            identity = self.context.get('offer_availability_identity')
            if identity:
                offer_availability = OfferAvailability.objects.filter(
                    identity=identity,
                    available=True
                )[start_range:end_range]

            else:
                offer_availability = None

        except Exception:
            logger.exception(''.join([
                'failed to get offers.'
            ]))

        tiles = []
        for a in offer_availability:
            tile = OfferTile()
            tiles.append(tile.render_template_fragment(RequestContext(
                request, {
                    'offer': a.offer,
                    'offer_action': offer_action
                }
            )))
        if not tiles:
            tile = DummyOfferTile()
            tiles = []
            tiles.append(tile.render_template_fragment(RequestContext(
                request, {
                    'identity': identity,
                    'current_identity': current_identity,
                }
            )))
        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles
        })
        return local_context

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

from knotis.views.mixins import (
    RenderTemplateFragmentMixin
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

from knotis.contrib.twitter.views import get_twitter_feed_json
from knotis.contrib.yelp.views import get_reviews_by_yelp_id
import json

from sorl.thumbnail import get_thumbnail

from knotis.views import AJAXFragmentView

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
        else:
            raise Exception('IdentityType not currently supported')

        context.update({
            'profile_markup': profile_view.render_template_fragment(context)
        })

        return context


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
            'knotis/identity/js/profile.js',
            'knotis/api/js/api.js',
            'knotis/identity/js/business-tile.js'
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
                    'identity': establishment,
                    'request': self.request
                })
                tiles.append(
                    establishment_tile.render_template_fragment(
                        establishment_context
                    )
                )

        local_context = copy.copy(self.context)
        local_context.update({
            'tiles': tiles,
            'tile_link_template': '/id/', # + identity.id
            'request': self.request
        })

        return local_context


class IdentityTile(FragmentView):
    template_name = 'knotis/identity/tile.html'
    view_name = 'identity_tile'

    def process_context(self):
        
        request = self.context.get('request')
        render_follow = False
        following = False
        if request.user.is_authenticated():
            current_identity_id = request.session.get('current_identity_id')
            current_identity = Identity.objects.get(
                pk=current_identity_id
            )
            render_follow = True

            follows = Relation.objects.get_following(current_identity)  
            business = self.context.get('identity')
            for follow in follows:
                if (not follow.deleted) and (follow.related.id == business.id):
                    following = True
                    break
        else:
            current_identity = None
            render_follow = False

        try:
            profile_badge_image = ImageInstance.objects.get(
                related_object_id=business.id,
                context='profile_badge',
                prrimary=True
            )
        except Exception, e:
            profile_badge_image = None

        try:
            profile_banner_image = ImageInstance.objects.get(
                related_object_id=business.id,
                context='profile_banner',
                primary=True
            )
        except Exception, e:
            profile_banner_image = None


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


class EstablishmentProfileOffers(FragmentView):
    template_name = 'knotis/identity/establishment_offers.html'
    view_name = 'establishment_offers'
    
    def process_context(self):
        request = self.request
        establishment_id = self.context.get('establishment_id')
        
        local_context = copy.copy(self.context)
        return local_context
        
class EstablishmentProfileContact(FragmentView):
    template_name = 'knotis/identity/establishment_contact.html'
    view_name = 'establishment_contact'
    
    def process_context(self):
        request = self.context.get('request')
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
        request = self.context.get('request')
        establishment_id = self.context.get('establishment_id')
        
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        business = IdentityBusiness.objects.get_establishment_parent(establishment)

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
        else:
            address = None

        local_context.update({
            'address': address,
            'address_latitude': locationItem[0].location.latitude,
            'address_longitude': locationItem[0].location.longitude
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

        endpoint_type_dict = {
            'twitter': EndpointTypes.TWITTER,
            'email': EndpointTypes.EMAIL,
            'phone': EndpointTypes.PHONE,
            'website': EndpointTypes.WEBSITE,
            'yelp': EndpointTypes.YELP,
            'facebook': EndpointTypes.FACEBOOK
        }

        updated_endpoints = []
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

                updated_endpoints.append(updated_endpoint)

        return self.generate_response({
            'updated_endpoints': map(endpoint_to_dict, updated_endpoints)
        })


class EstablishmentAboutTwitterFeed(FragmentView):
    template_name = 'knotis/identity/establishment_about_twitter.html'
    view_name = 'establishment_about_twitter'
    
    def process_context(self):
        request = self.context.get('request')
        establishment_id = self.context.get('establishment_id')
        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        business = IdentityBusiness.objects.get_establishment_parent(establishment)


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
            twitter_feed = json.loads(get_twitter_feed_json(twitter_endpoint['value']))
            local_context.update({
                'twitter_feed': twitter_feed
            })

        return local_context


class EstablishmentAboutYelpFeed(FragmentView):
    template_name = 'knotis/identity/establishment_about_yelp.html'
    view_name = 'establishment_about_yelp'

    def process_context(self):
        request = self.context.get('request')
        establishment_id = self.context.get('establishment_id')
        
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
        request = self.context.get('request')
        establishment_id = self.context.get('establishment_id')

        establishment = IdentityEstablishment.objects.get(pk=establishment_id)
        business = IdentityBusiness.objects.get_establishment_parent(establishment)

        images = ImageInstance.objects.filter(
            related_object_id=business.pk,
            context='business_profile_carousel',
            primary=False
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
        request = self.request
        establishment_id = self.context.get('establishment_id')
        
        local_context = copy.copy(self.context)
        local_context.update({
            'about_markup': EstablishmentAboutAbout().render_template_fragment(local_context),
            'twitter_markup': EstablishmentAboutTwitterFeed().render_template_fragment(local_context),
            'yelp_markup': EstablishmentAboutYelpFeed().render_template_fragment(local_context),
            'carousel_markup': EstablishmentAboutCarousel().render_template_fragment(local_context)
        })
        return local_context

get_class = lambda x: globals()[x]


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


            if establishment:
                business = IdentityBusiness.objects.get_establishment_parent(establishment)
            if not establishment:
                raise IdentityBusiness.DoesNotExist
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
            'geocomplete/jquery.geocomplete.min.js',
            'knotis/layout/js/forms.js',
            'knotis/maps/js/maps.js',
            'knotis/identity/js/profile.js',
            'knotis/identity/js/establishment_contact.js',
            'knotis/identity/js/establishment_about.js'
        ]

        profile_badge_image = None
        
        # if there is no profile badge on establishment check business
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
                identity=business,
                endpoint_type=endpoint_class.EndpointType
            )

            endpoint_type_name = EndpointTypeNames[endpoint_class.EndpointType]
            endpoint_type_name = endpoint_type_name.lower()

            if endpoint and endpoint.value:

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
                    'display': display,
                    'endpoint_type': endpoint_class.EndpointType
                }

                endpoints.append(fake_endpoint)

            else:
                endpoints.append({
                    'id': '',
                    'endpoint_type_name': endpoint_type_name,
                    'value': '',
                    'uri': '',
                    'display': '',
                    'endpoint_type': endpoint_class.EndpointType
                })

        # determine nav view
        nav_context = Context({ 
            'request': request,
            'establishment_id': establishment_id,
            'endpoints': endpoints,
            'is_manager': is_manager
        })
        if self.context.get('view_name') == 'contact':
            nav_top_content = EstablishmentProfileContact().render_template_fragment(nav_context)
        elif self.context.get('view_name') == 'offers':
            pass
        elif self.context.get('view_name') == 'about':
            nav_top_content = EstablishmentProfileAbout().render_template_fragment(nav_context)
        else:
            nav_top_content = None

        local_context = copy.copy(self.context)
        local_context.update({
            'establishment': establishment,
            'establishment_parent': business,
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
	    'top_menu_name': 'identity_profile',
            'nav_top_content': nav_top_content
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

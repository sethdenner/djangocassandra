import copy
from django import http
from django.conf import settings
from django.template import (
    RequestContext,
    Context
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import log
from knotis.utils.regex import REGEX_UUID
logger = log.getLogger(__name__)

from knotis.views import (
    EmbeddedView,
    ModalView,
    FragmentView,
    PaginationMixin,
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

from knotis.contrib.endpoint.models import EndpointIdentity
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin


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
        'knotis/layout/js/pagination.js',
        'knotis/identity/js/identity-action.js',
        'knotis/identity/js/business-tile.js',
        'knotis/identity/js/businesses.js',
    ]


class EstablishmentsGrid(
    GridSmallView,
    PaginationMixin,
    GetCurrentIdentityMixin
):
    view_name = 'establishments_grid'

    def get_queryset(self):
        current_identity = self.get_current_identity(self.request)

        establishments = IdentityEstablishment.objects.all()
        if (
            not current_identity or
            not current_identity.identity_type == IdentityTypes.SUPERUSER
        ):
            establishments = establishments.filter(
                available=True
            )

        return establishments

    def process_context(self):

        establishments = self.get_page(self.context)

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


class IdentityActionButton(ActionButton):
    view_name = 'identity_tile_action'

    def actions(self):
        tile_identity = self.context.get('identity')
        current_identity = self.context.get('current_identity')

        if not current_identity:
            href = '/signup/?close_href=/id/%s/' % tile_identity
            return [
                ButtonAction(
                    'Follow',
                    href,
                    {},
                    'get',
                    deep=True,
                )
            ]

        following = Relation.objects.follows(current_identity, tile_identity)
        is_following = len(following) == 0
        action_text = 'Follow' if is_following else 'Unfollow'
        return [
            ButtonAction(
                action_text,
                '/relation/following/',
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
        identity_tile_context = RequestContext(request, {
            'current_identity': current_identity,
            'identity': identity
        })

        if ((current_identity and
                current_identity.identity_type == IdentityTypes.INDIVIDUAL) or
                current_identity is None):
            action_button = IdentityActionButton()
            action_button_content = action_button.render_template_fragment(
                identity_tile_context
            )
        else:
            action_button_content = None

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
                errors['no-field'] = e.message

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
                errors['no-field'] = e.message

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
    template_name = 'knotis/transaction/tile.html'
    view_name = 'transaction_tile'

    def process_context(self):
        identity = self.context['identity']

        profile_badge_image = get_identity_profile_badge(identity)
        transaction = self.context.get('transaction')
        try:
            profile_banner_image = ImageInstance.objects.get(
                related_object_id=transaction.offer.id,
                context='offer_banner',
                primary=True
            )
        except:
            profile_banner_image = None

        profile_banner_color = get_identity_default_profile_banner_color(
            transaction.owner
        )
        self.context['offer'] = transaction.offer

        self.context.update({
            'badge_image': profile_badge_image,
            'banner_image': profile_banner_image,
            'profile_banner_color': profile_banner_color
        })

        return self.context

from django import http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    ListView
)
from django.shortcuts import (
    render,
    get_object_or_404
)
from django.utils import log
logger = log.getLogger(__name__)

from knotis.views.mixins import RenderTemplateFragmentMixin

from knotis.contrib.auth.models import UserInformation
from knotis.contrib.maps.forms import GeocompleteForm
from knotis.contrib.media.models import Image

from models import (
    Identity,
    IdentityIndividual,
    IdentityEstablishment
)

from forms import (
    IdentityIndividualSimpleForm,
    IdentityBusinessSimpleForm
)


class EstablishmentProfileView(View, RenderTemplateFragmentMixin):
    template_name = 'knotis/identity/profile_establishment.html'
    view_name = 'establishment_profile'

    def get(
        self,
        request,
        establishment_id=None,
        backend_name=None,
        *args,
        **kwargs
    ):
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
            individual = IdentityIndividual.objects.get_individual(
                request.user
            )
            establishments_managed = (
                IdentityEstablishment.objects.get_establishments(
                    individual
                )
            )

            for managed in establishments_managed:
                if managed.id == establishment.id:
                    is_manager = True
                    break

        styles = [
            'layout/css/header.css',
            'layout/css/grid.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'knotis/identity/css/profile.css',
            'styles/default/fileuploader.css'
        ]

        pre_scripts = []

        post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'layout/js/header.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js'
        ]

        images_establishment = Image.objects.filter(
            related_object_id=establishment.id
        )

        if 0 == images_establishment.count():
            no_logo = True
            if is_manager:
                profile_logo_uri = ''.join([
                    settings.STATIC_URL,
                    'knotis/identity/img/add_logo.png'
                ])

            else:
                profile_logo_uri = ''.join([
                    settings.STATIC_URL,
                    'knotis/identity/img/profile_default.png'
                ])

        else:
            no_logo = False
            profile_logo_uri = images_establishment[0].image.url

        return render(
            request,
            self.template_name, {
                'establishment': establishment,
                'is_manager': is_manager,
                'styles': styles,
                'pre_scripts': pre_scripts,
                'post_scripts': post_scripts,
                'profile_logo_uri': profile_logo_uri,
                'no_logo': no_logo
            }
        )


class FirstIdentityView(View, RenderTemplateFragmentMixin):
    template_name = 'knotis/identity/first.html'
    view_name = 'identity_edit'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        try:
            individual = IdentityIndividual.objects.get_individual(
                request.user
            )

        except:
            individual = None

        return render(
            request,
            self.template_name, {
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
            }
        )


class IdentitySwitcherView(ListView, RenderTemplateFragmentMixin):
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

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        current_identity = request.session.get('current_identity')
        if not current_identity:
            user_information = UserInformation.objects.get(user=request.user)
            current_identity = user_information.default_identity

        available_identities = Identity.objects.get_available(
            user=request.user
        )

        parameters = {
            'current': current_identity,
            'available': available_identities
        }

        return render(
            request,
            self.template_name,
            parameters
        )

    def put(
        self,
        request,
        identity_id,
        *args,
        **kwargs
    ):
        """
        Update current identity
        """
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

            request.session['current_identity'] = identity
            return http.HttpResponse('OK')

        except Exception, e:
            logger.exception(
                'identity with id=%s does not exist.' % identity_id
            )
            return http.HttpResponseServerError(e)

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        request = context.get('request')
        if not request:
            return ''

        if not request.user.is_authenticated():
            return ''

        key_available = 'available_identities'

        try:
            context[key_available] = Identity.objects.get_available(
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

        return super(
            IdentitySwitcherView,
            cls
        ).render_template_fragment(context)

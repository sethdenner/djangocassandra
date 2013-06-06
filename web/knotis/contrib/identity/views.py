from django import http
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
    ListView
)
from django.shortcuts import render
from django.utils import log
logger = log.getLogger(__name__)

from knotis.views.mixins import RenderTemplateFragmentMixin

from knotis.contrib.auth.models import UserInformation
from knotis.contrib.identity.models import Identity
from knotis.contrib.maps.forms import GeocompleteForm

from models import IdentityIndividual

from forms import (
    IdentityIndividualSimpleForm,
    IdentityBusinessSimpleForm
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
                    initial={'subject_id': individual.id}
                ),
                'location_form': GeocompleteForm()
            }
        )


class IdentitySwitcherView(ListView, RenderTemplateFragmentMixin):
    template_name = 'identity/switcher.html'
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

        try:
            context['available_identities'] = Identity.objects.get_available(
                user=request.user
            )

        except:
            logger.exception('failed to get available identities.')

        return super(
            IdentitySwitcherView,
            cls
        ).render_template_fragment(context)

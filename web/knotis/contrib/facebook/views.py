from django.shortcuts import (
    render,
    get_object_or_404
)

from django.conf import settings
from django.template import Context

from knotis.views import (
    FragmentView,
    AJAXView,
    AJAXFragmentView
)

from knotis.contrib.identity.models import Identity
from knotis.contrib.endpoint.forms import (
    EndpointForm,
    CredentialsForm
)
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes,
    Credentials
)
from knotis.contrib.endpoint.views import SocialIntegrationTile


class FacebookRevokeAccessView(AJAXView):
    def post(
        self,
        request
    ):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity_id']
        )

        endpoint_pk = request.POST.get('endpoint_pk')

        endpoint = Endpoint.objects.get(pk=endpoint_pk)

        if endpoint.identity != current_identity:
            return self.generate_response({
                'errors': {
                    'no-field': 'This endpoint does not belong to you.',
                    'status': 'ERROR'
                }
            })

        credentials = Credentials.objects.filter(endpoint=endpoint)

        errors = {}
        for credential in credentials:
            try:
                credential.delete()

            except:
                errors['no-field'] = 'Failed to revoke permissions.'
                break

        if errors:
            return self.generate_response({
                'errors': errors,
                'status': 'ERROR'
            })

        else:
            endpoint.delete()
            return self.generate_response({'status': 'OK', 'errors': None})


class FacebookSdkInitializationFragment(FragmentView):
    view_name = 'facebook_sdk_initialization'
    template_name = 'knotis/facebook/sdk_initialization.html'

    def process_context(self):
        local_context = Context()
        local_context['facebook_app_id'] = settings.FACEBOOK_APP_ID

        return local_context


class FacebookAccountChoiceFragment(AJAXFragmentView):
    view_name = 'facebook_account_choice'
    template_name = 'knotis/facebook/account_choice.html'

    def process_context(self):
        return self.context

    def post(self, request):
        current_identity = get_object_or_404(
            Identity,
            pk=request.session['current_identity_id']
        )
        endpoint_form = EndpointForm(
            data={
                'endpoint_type': EndpointTypes.FACEBOOK,
                'identity': current_identity.pk,
                'value': request.POST.get('account-name'),
                'context': 'facebook_publish',
                'primary': True,
                'validated': True
            }
        )

        if not endpoint_form.is_valid():
            errors = {}
            for field, messages in endpoint_form.errors.iteritems():
                errors[field] = [message for message in messages]
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        endpoint = endpoint_form.save()

        credentials_form = CredentialsForm(
            data={
                'endpoint': endpoint.pk,
                'identifier': request.POST.get('account-id'),
                'key': request.POST.get('access-token')
            }
        )

        if not credentials_form.is_valid():
            endpoint.delete()

            errors = {}
            for field, messages in endpoint_form.errors.iteritems():
                errors[field] = [message for message in messages]
            return self.generate_response({
                'status': 'ERROR',
                'errors': errors
            })

        credentials_form.save()

        facebook_tile = SocialIntegrationTile(
            service='facebook',
            endpoint=endpoint
        )
        return self.generate_response({
            'status': 'OK',
            'errors': None,
            'html': facebook_tile.render_template_fragment(Context({
                'STATIC_URL': settings.STATIC_URL
            }))
        })


def channel(request):
    return render(
        request,
        'channel.html',
        {}
    )


def get_facebook_avatar(facebook_id):
    if not facebook_id:
        return None

    return '/'.join([
        'http://graph.facebook.com',
        facebook_id,
        'picture'
    ])

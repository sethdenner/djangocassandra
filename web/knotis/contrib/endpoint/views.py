import copy

from django.conf import settings
from django.template import Context
from knotis.utils.email import (
    generate_email
)

from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes,
    Credentials
)
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.views import (
    AJAXView,
    FragmentView,
    EmbeddedView,
)
from knotis.contrib.layout.views import (
    GridSmallView,
    DefaultBaseView,
)


def send_validation_email(
    user_id,
    email_endpoint
):
    subject = 'Welcome to Knotis!'
    generate_email(
        'activate',
        subject,
        settings.EMAIL_HOST_USER,
        [email_endpoint.value], {
            'user_id': user_id,
            'validation_key': email_endpoint.validation_key,
            'BASE_URL': settings.BASE_URL,
            'STATIC_URL_ABSOLUTE': settings.STATIC_URL_ABSOLUTE,
            'SERVICE_NAME': settings.SERVICE_NAME
        }
    ).send()


class SocialIntegrationTile(FragmentView):
    template_name = 'knotis/endpoint/social_tile.html'
    view_name = 'social_tile'

    def __init__(
        self,
        service,
        endpoint=None,
        *args,
        **kwargs
    ):
        super(SocialIntegrationTile, self).__init__(
            *args,
            **kwargs
        )

        self.service = service
        self.endpoint = endpoint

    def process_context(self):
        self.context['service_name'] = self.service
        self.context['endpoint'] = self.endpoint

        return self.context


class SocialIntegrationsGridView(GridSmallView, GetCurrentIdentityMixin):
    view_name = 'social_integrations_grid'

    def process_context(self):
        request = self.context.get('request')
        current_identity = self.get_current_identity(request)

        facebook_tile = SocialIntegrationTile(service='facebook')
        twitter_tile = SocialIntegrationTile(service='twitter')

        tile_context = Context({
            'STATIC_URL': settings.STATIC_URL
        })

        self.context['tiles'] = [
            facebook_tile.render_template_fragment(tile_context),
            twitter_tile.render_template_fragment(tile_context),
        ]

        facebook_endpoints = Endpoint.objects.filter(
            identity=current_identity,
            endpoint_type=EndpointTypes.FACEBOOK
        )

        for endpoint in facebook_endpoints:
            connected_facebook = SocialIntegrationTile(
                service='facebook',
                endpoint=endpoint
            )
            self.context['tiles'].append(
                connected_facebook.render_template_fragment(tile_context)
            )

        twitter_endpoints = Endpoint.objects.filter(
            identity=current_identity,
            endpoint_type=EndpointTypes.TWITTER
        )

        for endpoint in twitter_endpoints:
            connected_twitter = SocialIntegrationTile(
                service='twitter',
                endpoint=endpoint
            )
            self.context['tiles'].append(
                connected_twitter.render_template_fragment(tile_context)
            )

        return self.context


class SocialMediaSettingsView(EmbeddedView):
    url_patterns = [r'^settings/social/$']
    default_parent_view_class = DefaultBaseView
    template_name = 'knotis/endpoint/social_media_settings.html'
    styles = [
        'knotis/endpoint/css/social_tile.css',
    ]
    post_scripts = [
        'knotis/endpoint/js/social_media.js'
    ]

    def process_context(self):
        local_context = copy.copy(self.context)
        local_context.update({
            'fixed_side_nav': True
        })
        return local_context


class DeleteEndpointView(AJAXView, GetCurrentIdentityMixin):
    def post(
        self,
        request
    ):
        current_identity = self.get_current_identity(request)

        endpoint_pk = request.POST.get('endpoint_pk')

        endpoint = Endpoint.objects.get(pk=endpoint_pk)

        if endpoint.identity != current_identity:
            return self.generate_ajax_response({
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
                errors['no-field'] = 'Failed to delete credentials.'
                break

        if errors:
            return self.generate_ajax_response({
                'errors': errors,
                'status': 'ERROR'
            })

        else:
            endpoint.delete()
            return self.generate_ajax_response(
                {'status': 'OK', 'errors': None}
            )

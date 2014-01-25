import copy

from django.conf import settings
from django.template import Context
from knotis.utils.email import (
    generate_email
)

from knotis.views import (
    ContextView,
    FragmentView
)
from knotis.contrib.layout.views import GridSmallView


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
        *args,
        **kwargs
    ):
        super(SocialIntegrationTile, self).__init__(
            *args,
            **kwargs
        )

        self.service = service

    def process_context(self):
        self.context['service_name'] = self.service

        return self.context


class SocialIntegrationsGridView(GridSmallView):
    view_name = 'social_integrations_grid'

    def process_context(self):
        facebook_tile = SocialIntegrationTile(service='facebook')
        twitter_tile = SocialIntegrationTile(service='twitter')

        tile_context = Context({
            'STATIC_URL': settings.STATIC_URL
        })

        self.context['tiles'] = [
            facebook_tile.render_template_fragment(tile_context),
            twitter_tile.render_template_fragment(tile_context),
        ]

        return self.context


class SocialMediaSettingsView(ContextView):
    template_name = 'knotis/endpoint/social_media_settings.html'

    def process_context(self):
        styles = self.context.get('styles', [])
        post_scripts = self.context.get('post_scripts', [])

        my_styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'knotis/endpoint/css/social_tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
        ]

        for style in my_styles:
            if not style in styles:
                styles.append(style)

        my_post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/header.js',
            'navigation/js/navigation.js',
            'knotis/endpoint/js/social_media.js'
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

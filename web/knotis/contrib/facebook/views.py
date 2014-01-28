import django.shortcuts as shortcuts

from django.conf import settings
from django.template import Context

from knotis.views import (
    FragmentView,
    AJAXFragmentView
)


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
        return self.generate_response({})


def channel(request):
    return shortcuts.render(
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

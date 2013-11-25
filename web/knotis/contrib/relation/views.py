from knotis.views import EmailView
import copy


class NewPermissionEmailBody(EmailView):
    template_name = 'knotis/relation/email_new_permission.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'http://example.com'
        initiator = 'Fine Bitstrings'
        confirm_link = 'http://example.com'

        local_context.update({
            'browser_link': browser_link,
            'initiator': initiator,
            'confirm_link': confirm_link
        })

        return local_context


class NewFollowerEmailBody(EmailView):
    template_name = 'knotis/relation/email_new_follower.html'

    def process_context(self):
        local_context = copy.copy(self.context)

        browser_link = 'example.com'
        business_name = 'Fine Bitstrings'
        business_cover_url = '/media/cache/ef/25/ef2517885c028d7545f13f79e5b7993a.jpg'
        business_logo_url = '/media/cache/87/08/87087ae77f4a298e550fc9d255513ad4.jpg'
        username = '@username'
        view_profile_link = 'example.com'

        local_context.update({
            'browser_link': browser_link,
            'business_cover_url': business_cover_url,
            'business_logo_url': business_logo_url,
            'business_name': business_name,
            'username': username,
            'view_profile_link': view_profile_link
        })

        return local_context

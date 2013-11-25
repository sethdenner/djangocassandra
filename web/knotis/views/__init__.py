from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import (
    login_required as auth_login_required
)

from django.http import QueryDict
from django.views.generic import (
    View,
    TemplateView
)
from django.conf.urls.defaults import url
from django.template import (
    RequestContext
)

from mixins import (
    RenderTemplateFragmentMixin,
    GenerateAJAXResponseMixin
)

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import copy

class ContextView(TemplateView):
    '''
    Slight modification to the behavior of TemplateView.
    The dispatch method now creates a context upon all requests
    and copys the kwargs dict to the new request context.

    get_context_data now just returns self.context
    '''
    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):
        self.context = RequestContext(request)
        self.context.update(kwargs)

        return super(ContextView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def process_context(self):
        '''
        Override this method to make further modifications
        to the context on a per view basis.
        '''
        return self.context

    def get_context_data(
        self,
        **kwargs
    ):
        return self.process_context()


class FragmentView(
    ContextView,
    RenderTemplateFragmentMixin
):
    def render_template_fragment(
        self,
        context
    ):
        self.context = context
        self.request = context.get('request')

        processed_context = self.process_context()
        return super(FragmentView, self).render_template_fragment(
            processed_context
        )



import httplib, urllib2, cgi
class EmailView(FragmentView):

    text_template_name = None
    
    def generate_email(self, subject, from_email, to_list, context):
        context = copy.copy(context)

        context.update({
            'email_type': 'html'
        })
        html_content = self.render_template_fragment(context)

        params = {
            'page': html_content
        }
            
        # req = urllib2.Request('http://192.168.1.103:16081/premail/', params)
        # fweb = urllib2.urlopen(req)
        # html_content = fweb.read()

        # import pdb; pdb.set_trace()
        
        context.update({
            'email_type': 'text'
        })
        text_content = self.render_template_fragment(context)
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
        msg.attach_alternative(html_content, 'text/html')

        return msg
  
    
class AJAXView(
    View,
    GenerateAJAXResponseMixin
):
    pass


class AJAXFragmentView(
    FragmentView,
    GenerateAJAXResponseMixin
):
    pass


class ApiView(AJAXView):
    api_url = None
    api_version = 'v1'

    @csrf_exempt
    @never_cache
    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):
        """
        This needs to check for authorization either
        the user needs to be logged in or oauth access
        token must be present. maybe should make public/private
        be a flag on the Api Class.
        """

        method = request.method.lower()

        if 'put' == method:
            request.PUT = QueryDict(request.raw_post_data)

        if 'delete' == method:
            request.DELETE = QueryDict(request.raw_post_data)

        return super(ApiView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    @classmethod
    def urls(
        cls,
        login_required=False
    ):
        if None == cls.api_url:
            raise Exception('must define a url for ApiView')

        if login_required:
            view = auth_login_required(cls.as_view())

        else:
            view = cls.as_view()

        return url(
            '/'.join([
                '^api',
                ApiView.api_version,
                cls.api_url,
                '$'
            ]),
            view
        )

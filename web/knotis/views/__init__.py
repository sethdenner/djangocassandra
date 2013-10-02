from django.views.decorators.csrf import csrf_exempt

from django.http import QueryDict
from django.views.generic import (
    View,
    TemplateView
)
from django.conf.urls.defaults import url
from django.template import (
    Context,
    RequestContext
)

from mixins import (
    RenderTemplateFragmentMixin,
    GenerateAJAXResponseMixin
)


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
    model = None
    api_url = None
    api_version = 'v1'

    @csrf_exempt
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
    def urls(cls):
        if None == cls.model:
            raise Exception('must define a model for ApiView')

        api_url = (
            cls.api_url if cls.api_url else cls.model.__name__.lower()
        )

        return url(
            '/'.join([
                '^api',
                ApiView.api_version,
                cls.model._meta.app_label,
                api_url,
                ''
            ]),
            cls.as_view()
        )

from django.http import QueryDict
from django.views.generic import View
from django.conf.urls.defaults import url
from django.template import RequestContext

from mixins import (
    RenderTemplateFragmentMixin,
    GenerateAJAXResponseMixin
)


class FragmentView(
    View,
    RenderTemplateFragmentMixin
):
    pass


class AJAXView(
    View,
    GenerateAJAXResponseMixin
):
    pass


class AJAXFragmentView(
    View,
    RenderTemplateFragmentMixin,
    GenerateAJAXResponseMixin
):
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.render_ajax_fragment(request, *args, **kwargs)

    @classmethod
    def render_ajax_fragment(
        cls,
        request,
        *args,
        **kwargs
    ):
        context = RequestContext(request)
        context['args'] = args
        context['kwargs'] = kwargs
        return cls.generate_response({
            'html': cls.render_template_fragment(context)
        })


class ApiView(AJAXView):
    model = None
    api_url = None
    api_version = 'v1'

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

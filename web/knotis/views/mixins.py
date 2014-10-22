import sys
import imp
import inspect
import json

from django.conf import settings
from django.conf.urls.defaults import (
    patterns,
    url
)

from django.template.loader import (
    get_template,
    render_to_string
)

from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponseServerError
)

from django.views.decorators.csrf import csrf_exempt


class RenderTemplateFragmentMixin(object):
    registered_fragments = {}
    template_name = None
    view_name = None

    def render_template_fragment(
        self,
        context
    ):
        template = get_template(self.template_name)
        return template.render(context)

    @classmethod
    def register_template_fragment(cls):
        RenderTemplateFragmentMixin.registered_fragments[
            cls.view_name
        ] = cls

    @staticmethod
    def register_template_fragment_views(apps=None):
        """
        Register classes in views modules of installed apps
        that implement RenderTemplateFragmentMixin.

        Param: apps - iterable of strings representing module names.
        """
        if not apps:
            apps = settings.INSTALLED_APPS

        for app in apps:
            view_module_name = '.'.join([
                app,
                'views'
            ])
            if view_module_name in sys.modules:
                view_module = sys.modules[view_module_name]

            else:
                try:
                    file, filepath, description = None, None, None
                    for name in view_module_name.split('.'):
                        file, filepath, description = imp.find_module(
                            name,
                            [filepath] if filepath else sys.path
                        )

                        if file:
                            break

                except ImportError:
                    continue

                try:
                    view_module = imp.load_module(
                        view_module_name,
                        file,
                        filepath,
                        description
                    )

                except ImportError:
                    continue

            if not view_module:
                continue

            class_members = inspect.getmembers(
                view_module,
                inspect.isclass
            )

            for c in class_members:
                name, cls = c
                if issubclass(
                    cls,
                    RenderTemplateFragmentMixin
                ) and (
                    cls.__name__ != RenderTemplateFragmentMixin.__name__
                ):
                    cls.register_template_fragment()


class GenerateRedirectResponseMixin(object):
    def generate_redirect_response(
        self,
        redirect_url,
        permanent=False
    ):
        if permanent:
            response_class = HttpResponsePermanentRedirect

        else:
            response_class = HttpResponseRedirect

        return response_class(
            redirect_url
        )


class GenerateHtmlResponseMixin(object):
    def generate_html_response(
        self,
        context,
        template_name,
        **response_kwargs
    ):
        return HttpResponse(
            render_to_string(
                template_name,
                context_instance=context
            ),
            content_type='text/html'
        )


class GenerateAjaxResponseMixin(object):
    def generate_ajax_response(
        self,
        data,
        format='json'
    ):
        if format == 'json':
            return HttpResponse(
                json.dumps(data),
                content_type='application/json'
            )

        else:
            return HttpResponseServerError(''.join([
                self.__class__.__name__,
                ' does not support response format <',
                format,
                '>.'
            ]))


class GenerateApiUrlsMixin(object):
    API_VERSION_MIN = 0
    resource_name = None
    api_path = None
    api_version = 'v%s' % (API_VERSION_MIN,)

    @classmethod
    def urls(cls):
        if None == cls.api_path:
            raise Exception('must define a path for this api.')

        if hasattr(cls, 'router_class'):
            router = cls.router_class()
            router.register(
                r'/'.join([
                    'api',
                    cls.api_version,
                    cls.api_path
                ]),
                cls,
                base_name=cls.resource_name
            )
            return router.urls

        else:
            view = cls.as_view()
            return patterns(
                '',
                url(
                    r'/'.join([
                        '^api',
                        cls.api_version,
                        cls.api_path,
                        '$'
                    ]),
                    csrf_exempt(view)
                )
            )


class PaginationMixin(object):
    queryset = None
    page_key = 'page'
    count_key = 'count'
    default_count = 24

    @staticmethod
    def get_request_parameter(
        context,
        key,
        default=None
    ):
        '''
        This method is responsible for pulling out the paginaiton parameters
        from a RequestContext object.
        '''
        value = context.get(key, default)

        request = context.get('request')
        if None is not request:
            value = request.GET.get(key, value)
            value = request.POST.get(key, value)

        return value

    def get_page(
        self,
        context,
        page=None,
        count=None
    ):
        if None is page:
            page = self.get_request_parameter(
                context,
                self.page_key
            )
            if None is page:
                page = 1

            else:
                page = int(page)

        if None is count:
            count = self.get_request_parameter(
                context,
                self.count_key
            )
            if None is count:
                count = self.default_count

            else:
                count = int(count)

        start = (page - 1) * count
        stop = start + count
        return self.get_queryset()[start:stop]

    def get_queryset(self):
        '''
        Override if you need a dynamic queryset
        '''
        return self.queryset

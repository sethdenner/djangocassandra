import re
import copy
import warnings

from django.conf.urls.defaults import (
    patterns,
    url
)
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    View as DjangoView,
    TemplateView
)
from django.template import (
    Context,
    RequestContext
)
from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives
from django.http import (
    HttpResponseServerError
)


from rest_framework.views import APIView as RestApiView
from rest_framework.viewsets import (
    ViewSet,
    ModelViewSet
)
from rest_framework.routers import DefaultRouter

from .mixins import (
    RenderTemplateFragmentMixin,
    GenerateAjaxResponseMixin,
    GenerateHtmlResponseMixin,
    GenerateRedirectResponseMixin,
    GenerateApiUrlsMixin
)


class ContextView(TemplateView):
    '''
    Slight modification to the behavior of TemplateView.
    The dispatch method now creates a context upon all requests
    and copys the kwargs dict to the new request context.

    get_context_data now just returns self.context
    '''
    def __init__(
        self,
        context=None,
        *args,
        **kwargs
    ):
        if context is None:
            self.context = Context()
        else:
            self.context = context

        super(ContextView, self).__init__(
            *args,
            **kwargs
        )

    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):
        self.request = request
        self.context = RequestContext(
            request,
            kwargs
        )

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

    def update_context(
        self,
        other={}
    ):
        if isinstance(other, Context):
            flattened_context = {}
            for d in reversed(other.dicts):
                flattened_context.update(d)

            self.context.update(flattened_context)

        elif isinstance(other, dict):
            self.context.update(other)

        else:
            raise Exception(
                'Can only update context with dict or context object'
            )

        return self.context


class FragmentView(
    ContextView,
    RenderTemplateFragmentMixin
):
    def render_template_fragment(
        self,
        context
    ):
        self.update_context(context)
        self.request = context.get('request')

        processed_context = self.process_context()
        return super(FragmentView, self).render_template_fragment(
            processed_context
        )


class EmbeddedView(
    FragmentView,
    GenerateAjaxResponseMixin,
    GenerateHtmlResponseMixin,
    GenerateRedirectResponseMixin
):
    '''
    The EmbeddedView class provides support for rendering a view that is
    intended to be rendered as a sub-view of a parent view potentially
    after fetching it with an AJAX request.

    However it is sometimes desired make a request to the view that
    originates from a context other than the one the view is normally
    rendered in. In this case the parent view that the markup is normally
    embedded in needs to also be rendered and returned in the response.
    '''

    url_patterns = None
    default_parent_view_class = None
    template_placeholders = ['content']
    parent_template_placeholder = None
    default_target_element_id = 'main-content'

    styles = []
    pre_scripts = []
    post_scripts = []

    class RESPONSE_FORMATS(object):
        HTML = 'html'
        REDIRECT = 'redirect'

        class AJAX(object):
            JSON = 'json'
            DEFAULT = JSON

        @classmethod
        def is_ajax(cls, response_format):
            response_format = response_format.lower()
            return (
                response_format in
                cls.AJAX.__dict__.values()
            )

    @classmethod
    def get_response_format(cls, request):
        response_format = (
            request.GET.get(
                'format',
                cls.RESPONSE_FORMATS.HTML
            ).lower()
        )
        response_format = (
            request.POST.get('format', response_format).lower()
        )

        return response_format

    @classmethod
    def get_target_element_id(cls, request):
        target_element_id = (
            request.GET.get('teid', cls.default_target_element_id)
        )
        target_element_id = (
            request.POST.get('teid', target_element_id)
        )

        return target_element_id

    @staticmethod
    def get_parent_view():
        pass

    @staticmethod
    def url_path_to_dict(path):
        if not path:
            path = ''

        pattern = (
            r'^'
            r'((?P<schema>.+?)://)?'
            r'((?P<user>.+?)(:(?P<password>.*?))?@)?'
            r'(?P<host>.*?)'
            r'(:(?P<port>\d+?))?'
            r'(?P<path>/.*?)?'
            r'(?P<query>[?].*?)?'
            r'$'
        )

        regex = re.compile(pattern)
        m = regex.match(path)
        d = m.groupdict() if m is not None else None

        return d

    def __init__(
        self,
        parent_view_class=None,
        parent_template_placeholder=None,
        *args,
        **kwargs
    ):
        if parent_view_class:
            self.parent_view_class = parent_view_class

        else:
            self.parent_view_class = self.default_parent_view_class

        if self.parent_view_class:
            if None is not parent_template_placeholder:
                self.parent_template_placeholder = parent_template_placeholder

            elif None is self.parent_template_placeholder:
                self.parent_template_placeholder = (
                    self.parent_view_class.template_placeholders[0]
                )

        context = kwargs.pop('context', None)
        if not context:
            request = kwargs.get('request')
            if request:
                context = RequestContext(request)

            else:
                context = Context()

        super(EmbeddedView, self).__init__(
            context=context,
            *args,
            **kwargs
        )

    def dispatch(
        self,
        request,
        *args,
        **kwargs
    ):

        self.response_format = self.get_response_format(request)
        self.target_element_id = self.get_target_element_id(request)

        return super(EmbeddedView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def render_to_response(
        self,
        context=None,
        data={},
        errors={},
        render_template=True,
        **response_kwargs
    ):
        if not context:
            context = self.context

        if not isinstance(context, Context):
            context = RequestContext(
                self.request,
                context
            )

        if not hasattr(self, 'response_format'):
            self.response_format = self.get_response_format(self.request)

        if not hasattr(self, 'target_element_id'):
            self.target_element_id = self.get_target_element_id(self.request)

        context['format'] = self.response_format
        post_scripts = context.get('post_scripts', [])
        context['post_scripts'] = post_scripts + self.post_scripts
        pre_scripts = context.get('pre_scripts', [])
        context['pre_scripts'] = pre_scripts + self.pre_scripts
        styles = context.get('styles', [])
        context['styles'] = styles + self.styles

        if self.RESPONSE_FORMATS.is_ajax(self.response_format):
            if errors:
                data['errors'] = errors

            if render_template:
                data['html'] = render_to_string(
                    self.get_template_names()[0],
                    context_instance=context
                )
                data['targetid'] = self.target_element_id

            return self.generate_ajax_response(
                data=data,
                format=self.response_format
            )

        elif self.response_format == self.RESPONSE_FORMATS.HTML:
            if data:
                context['data'] = data

            if errors:
                context['errors'] = errors

            if None is self.parent_view_class:
                return self.generate_html_response(
                    context,
                    self.get_template_names()[0]
                )

            else:
                if (
                    not self.parent_template_placeholder in
                    self.parent_view_class.template_placeholders
                ):
                    warnings.warn(''.join([
                        'WARNING!: The parent view class ',
                        self.parent_view_class.__name__,
                        ' has does not define "',
                        self.parent_template_placeholder,
                        '" as a template placeholder!'
                    ]))

                context[self.parent_template_placeholder] = render_to_string(
                    self.get_template_names()[0],
                    context_instance=context
                )

                parent_instance = self.parent_view_class(
                    context=context,
                    request=self.request
                )

                parent_context = parent_instance.get_context_data()
                return parent_instance.render_to_response(
                    parent_context,
                    **response_kwargs
                )

        elif self.response_format == self.RESPONSE_FORMATS.REDIRECT:
            if 'next' not in data.keys:
                next_url = self.request.GET.get('next', '/')
                next_url = self.reqeust.POST.get('next', next_url)

            else:
                next_url = data.get('next', '/')

            next_url_dict = self.url_path_to_dict(next_url)
            next_url_relative = next_url_dict.get('path', '/')

            return self.generate_redirect_response(next_url_relative)

        else:
            return HttpResponseServerError(''.join([
                self.__class__.__name__,
                ' does not support response format <',
                self.response_format,
                '>.'
            ]))

    @classmethod
    def urls(
        cls,
        require_login=False
    ):
        '''
        This method returns a urlpatterns value to be used in url.py files.
        '''
        if not cls.url_patterns:
            raise cls.UrlPatternsUndefinedException(cls)

        if require_login:
            view = login_required(cls.as_view())

        else:
            view = cls.as_view()

        view_patterns = patterns('')
        for u in cls.url_patterns:
            view_patterns += patterns(
                '',
                url(
                    u,
                    view
                )
            )

        return view_patterns

    class UrlPatternsUndefinedException(Exception):
        def __init__(
            self,
            view_class
        ):
            self.view_class = view_class

        def __str__(self):
            return ''.join([
                'The View class ',
                self.view_class.__name__,
                'has no urls defined.'
            ])


class ModalView(EmbeddedView):
    default_close_href = '/'
    parent_template_placeholder = 'modal_content'

    def process_context(self):
        close_href_dict  = self.url_path_to_dict(
            self.request.GET.get(
                'close',
                self.default_close_href
            )
        )

        self.context.update({
            'close_href': close_href_dict.get(
                'path',
                self.default_close_href
            )
        })

        return self.context

    def render_to_response(
        self,
        context=None,
        data=None,
        **response_kwargs
    ):
        if None is data:
            data = {}

        data['modal'] = True

        return super(ModalView, self).render_to_response(
            context=context,
            data=data,
            **response_kwargs
        )


class EmailView(FragmentView):
    text_template_name = None

    def generate_email(self, subject, from_email, to_list, context):
        context = copy.copy(context)

        context.update({
            'email_type': 'html'
        })
        html_content = self.render_template_fragment(context)

        context.update({
            'email_type': 'text'
        })
        text_content = self.render_template_fragment(context)

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_list
        )
        msg.attach_alternative(html_content, 'text/html')

        return msg


class AJAXView(
    DjangoView,
    GenerateAjaxResponseMixin
):
    pass


class AJAXFragmentView(
    FragmentView,
    GenerateAjaxResponseMixin
):
    pass


class ApiViewSet(ViewSet, GenerateApiUrlsMixin):
    router_class = DefaultRouter


class ApiModelViewSet(ModelViewSet, GenerateApiUrlsMixin):
    router_class = DefaultRouter

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(ApiModelViewSet, self).__init__(
            *args,
            **kwargs
        )

        if not self.model:
            if self.queryset:
                self.model = self.queryset.model

    def get_queryset(self):
        queryset = super(ApiModelViewSet, self).get_queryset()
        if not self.model:
            return queryset

        query_params = self.request.QUERY_PARAMS

        field_names = self.model._meta.get_all_field_names()
        filter_params = {}
        for key, value in query_params.iteritems():
            if key in field_names:
                field = self.model._meta.get_field(key)
                if field.db_index:
                    filter_params[key] = field.to_python(value)

        if filter_params:
            queryset = queryset.filter(**filter_params)

        return queryset


class ApiView(RestApiView, GenerateApiUrlsMixin, GenerateAjaxResponseMixin):
    '''
    TODO: Need to remove GenerateAjaxResponseMixin once all the legacy api's
          are ported to rest_framework
    '''
    pass

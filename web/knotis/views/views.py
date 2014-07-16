import copy
import warnings

from django.conf.urls.defaults import (
    patterns,
    url
)
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


from rest_framework.views import APIView as RestApiView
from rest_framework.viewsets import (
    ViewSet,
    ModelViewSet
)
from rest_framework.routers import DefaultRouter

from .mixins import (
    RenderTemplateFragmentMixin,
    GenerateAJAXResponseMixin,
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
        context=Context(),
        *args,
        **kwargs
    ):
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


class EmbeddedView(FragmentView):
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

        if self.parent_view_class and None is parent_template_placeholder:
            self.parent_template_placeholder = (
                self.parent_view_class.template_placeholders[0]
            )

        else:
            self.parent_template_placeholder = parent_template_placeholder

        super(EmbeddedView, self).__init__(
            *args,
            **kwargs
        )

    def render_to_response(
        self,
        context,
        **response_kwargs
    ):
        self.update_context(context)

        response_format = self.context.get('format')
        if response_format == 'ajax' or None is self.parent_view_class:
            return super(EmbeddedView, self).render_to_response(
                context,
                **response_kwargs
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
                context
            )

            parent_instance = self.parent_view_class(**{
                'request': self.request
            })
            return parent_instance.render_to_response(
                context,
                **response_kwargs
            )

    @classmethod
    def urls(cls):
        '''
        This method returns a urlpatterns value to be used in url.py files.
        '''
        if not cls.url_patterns:
            raise cls.UrlPatternsUndefinedException(cls)

        view_patterns = patterns('')
        for u in cls.url_patterns:
            if '$' == u[-1]:
                view_url = ''.join([
                    u[:-1],
                    '((?P<format>.+)/)?',
                    u[-1:]
                ])

            else:
                view_url = ''.join([
                    u,
                    '((?P<format>.+)/)?'
                ])

            view_patterns += patterns(
                '',
                url(
                    view_url,
                    cls.as_view()
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
    '''
    The ModalView class provides support for rendering a view that is
    intended to be displayed in a modal dialog box after fetching it
    with an AJAX request.
    '''
    parent_view = None


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
    GenerateAJAXResponseMixin
):
    pass


class AJAXFragmentView(
    FragmentView,
    GenerateAJAXResponseMixin
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


class ApiView(RestApiView, GenerateApiUrlsMixin, GenerateAJAXResponseMixin):
    '''
    TODO: Need to remove GenerateAJAXResponseMixin once all the legacy api's
          are ported to rest_framework
    '''
    pass

import copy

from django.views.generic import (
    View,
    TemplateView
)
from django.template import (
    RequestContext
)

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
    View,
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
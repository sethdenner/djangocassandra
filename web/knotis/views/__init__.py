import json

from django.http import (
    QueryDict,
    HttpResponse,
    HttpResponseServerError
)
from django.views.generic import View
from django.conf.urls.defaults import url


class ApiView(View):
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

    @staticmethod
    def generate_response(
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
                'ApiView does not support response format <',
                format,
                '>.'
            ]))

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

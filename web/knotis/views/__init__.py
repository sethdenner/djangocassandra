from django.views.generic import View
from django.conf.urls.defaults import url
from django.http import HttpResponseServerError


class ApiView(View):
    model = None
    api_version = 'v1'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('Not implemented.')

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('Not implemented.')

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('Not implemented.')

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('Not implemented.')

    @classmethod
    def urls(cls):
        if None == cls.model:
            raise Exception('must define a model for ApiView')

        return url(
            '/'.join([
                '^api',
                cls.api_version,
                cls.model._meta.app_label,
                cls.model.__name__.lower(),
                ''
            ]),
            cls.as_view()
        )

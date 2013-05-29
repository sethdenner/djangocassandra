from django.http import HttpResponseServerError
from django.views.generic import View
from django.conf.urls.defaults import url


class ApiView(View):
    model = None
    model_name = None
    api_version = 'v1'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.create(
            request,
            *args,
            **kwargs
        )

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('create not implemented')

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.read(
            request,
            *args,
            **kwargs
        )

    def read(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('read not implemented')

    def put(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.update(
            self,
            request,
            *args,
            **kwargs
        )

    def patch(
        self,
        request,
        *args,
        **kwargs
    ):
        return self.update(
            self,
            request,
            *args,
            **kwargs
        )

    def update(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('update not implemented')

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponseServerError('delete not implemented')

    @classmethod
    def urls(cls):
        if None == cls.model:
            raise Exception('must define a model for ApiView')

        model_name = (
            cls.model_name if cls.model_name else cls.model.__name__.lower()
        )

        return url(
            '/'.join([
                '^api',
                ApiView.api_version,
                cls.model._meta.app_label,
                model_name,
                ''
            ]),
            cls.as_view()
        )

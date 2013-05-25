from django.views.generic import View
from django.conf.urls.defaults import url


class ApiView(View):
    model = None
    model_name = None
    api_version = 'v1'

    @classmethod
    def urls(cls):
        if None == cls.model:
            raise Exception('must define a model for ApiView')

        model_name = (
            cls.model_name if cls.model_name else cls.model.__name__.lower
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

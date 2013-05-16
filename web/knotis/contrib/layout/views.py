from django.views.generic import View
from django.shortcuts import render

from knotis.views.mixins import RenderTemplateFragmentMixin

class HeaderView(View, RenderTemplateFragmentMixin):
    template_name = 'layout/header.html'
    view_name = 'header'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return render(
            request,
            self.template_name,
            {}
        )

class IndexView(View):
    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        context = {
            'styles': ['layout/css/header.css']
        }

        return render(
            request,
            'layout/index.html',
            context
        )

from django.views.generic import View
from django.shortcuts import render

from knotis.views.mixins import RenderTemplateFragmentMixin

from forms import SearchForm


class SearchBarView(View, RenderTemplateFragmentMixin):
    template_name = 'search/search_bar.html'
    view_name = 'search_bar'

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        return render(
            request,
            self.template_name, {
                'search_form': SearchForm()
            }
        )

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return http.HttpResponse('OK')

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        context['search_form'] = SearchForm()

        return super(
            SearchBarView,
            cls
        ).render_template_fragment(context)

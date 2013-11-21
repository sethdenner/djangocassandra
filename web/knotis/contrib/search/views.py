import copy

from django.http import HttpResponse

from knotis.views import FragmentView

from forms import SearchForm

class SearchBarView(FragmentView):
    template_name = 'search/search_bar.html'
    view_name = 'search_bar'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponse('OK')

    def process_context(self):
        local_context = copy.copy(self.context)
        local_context.update({
            'search_form': SearchForm()
        })

        return local_context

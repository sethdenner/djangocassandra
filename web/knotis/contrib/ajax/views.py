from knotis.views import FragmentView


class Loading(FragmentView):
    view_name = 'loading'
    template_name = 'knotis/ajax/loading.html'

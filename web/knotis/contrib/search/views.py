import copy

from django.http import HttpResponse
from django.template import Context

#from haystack.views import SearchView
from haystack.query import SearchQuerySet

from knotis.contrib.identity.views import IdentityTile
from knotis.contrib.layout.views import GridSmallView
from knotis.views import FragmentView

from forms import SearchForm

class SearchResultsView(FragmentView):
    template_name = 'search/search.html'
    view_name = 'search_results'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        return HttpResponse('OK')

    def process_context(self):
        styles = self.context.get('styles', [])
        post_scripts = self.context.get('post_scripts', [])

        my_styles = [
            'knotis/layout/css/global.css',
            'knotis/layout/css/header.css',
            'knotis/layout/css/grid.css',
            'knotis/layout/css/tile.css',
            'navigation/css/nav_top.css',
            'navigation/css/nav_side.css',
            'styles/default/fileuploader.css'
        ]

        for style in my_styles:
            if not style in styles:
                styles.append(style)

        my_post_scripts = [
            'knotis/layout/js/layout.js',
            'knotis/layout/js/forms.js',
            'knotis/layout/js/header.js',
            'knotis/layout/js/create.js',
            'navigation/js/navigation.js',
            'jcrop/js/jquery.Jcrop.js',
            'scripts/fileuploader.js',
            'scripts/jquery.colorbox.js',
            'scripts/jquery.sickle.js',
            'knotis/identity/js/profile.js',
            'knotis/api/js/api.js',
            'knotis/identity/js/business-tile.js',
            'knotis/identity/js/businesses.js'
        ]

        for script in my_post_scripts:
            if not script in post_scripts:
                post_scripts.append(script)
        
        local_context = copy.copy(self.context)
        local_context.update({
            'styles': styles,
            'post_scripts': post_scripts,
            'fixed_side_nav': True,
        })

        return local_context


class SearchResultsGrid(GridSmallView):
    view_name = 'search_results_grid'

    def process_context(self):
        #page = int(self.context.get('page', '0'))
        #count = int(self.context.get('count', '20'))
        #start_range = page * count
        #end_range = start_range + count
        #businesses = IdentityBusiness.objects.all()[start_range:end_range]

        query = self.request.GET.get('q',None)
        if query:
            search_results = SearchQuerySet().filter(content=query)
            tiles = []

        else:
            tiles = []
            search_results = None
           
        if search_results:
            for result in search_results:
                business_tile = IdentityTile()
                result_context = Context({
                    'identity': result.object,
                    'request': self.request
                })
                tiles.append(
                    business_tile.render_template_fragment(
                        result_context
                    )
                )


        local_context = copy.copy(self.context)
        local_context.update({
            'tile_link_template': '/id/',  # + identity.id
            'request': self.request,
            'tiles': tiles,
            'search_results': search_results,
            'query': query
        })

        return local_context


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

import copy

from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from django.template import Context

from django.utils.log import logging
logger = logging.getLogger(__name__)

#from haystack.views import SearchView
from haystack.query import SearchQuerySet

from knotis.contrib.identity.views import IdentityTile
from knotis.contrib.offer.views import OfferTile
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
            'knotis/search/js/searchresults.js',
            'knotis/identity/js/business-tile.js'
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
        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count

        query = self.request.GET.get('q',None)
        if query:
            search_results = SearchQuerySet().filter(content=query)[start_range:end_range]
            tiles = []

        else:
            tiles = []
            search_results = None
           
        if search_results:
            i = 0
            for result in search_results:
                #if result.object.content_type == ContentType.objects.get('identity establishment'):
                if result.object.content_type.name == 'identity establishment':
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
                elif result.object.content_type == 'offer': 
                    offer_tile = OfferTile()
                    result_context = Context({
                        'offer': result.object,
                        'request': self.request
                    })
                    tiles.append(
                        offer_tile.render_template_fragment(
                            result_context
                        )
                    )
                    pass
                else:
                    #tiles.append( "no template for this object type" )
                    logger.exception(' no template available for this search result type. ')
    
        if not len(tiles):
            tiles.append("Sorry your search returned no results.")

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
        form_args = {}
        search_query = self.request.GET.get('q',None)
        if search_query:
            form_args['q'] = search_query

        local_context = copy.copy(self.context)
        local_context.update({
            'search_form': SearchForm(form_args),
            'search_query': search_query
        })

        return local_context

import copy

from django.http import HttpResponse

from django.template import Context

from django.utils.log import logging
logger = logging.getLogger(__name__)

#from haystack.views import SearchView

from knotis.contrib.identity.views import IdentityTile, get_current_identity
from knotis.contrib.offer.views import OfferTile
from knotis.contrib.layout.views import GridSmallView, DefaultBaseView
from knotis.contrib.search.api import SearchApi
from knotis.views import EmbeddedView


class SearchResultsView(EmbeddedView):
    default_parent_view_class = DefaultBaseView
    url_patterns = [
        r'^search/',
    ]
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
        search_query = self.context.get('q', None)

        return self.context.update({
            'search_query': search_query,
        })


class SearchResultsGrid(GridSmallView):
    view_name = 'search_results_grid'

    def process_context(self):
        page = int(self.context.get('page', '0'))
        count = int(self.context.get('count', '20'))
        start_range = page * count
        end_range = start_range + count

        query = self.request.GET.get('q',None)

        try:
            current_identity = get_current_identity(self.request)
        except:
            current_identity = None

        search_results = SearchApi.search(
            query,
            identity=current_identity
        )

        if search_results is not None:
            search_results = search_results[start_range:end_range]
            search_results = [x.object for x in search_results]

        tiles = []

        for result in search_results:
            try:
                if result.content_type.name == 'identity establishment':
                    business_tile = IdentityTile()
                    result_context = Context({
                        'identity': result,
                        'request': self.request
                    })
                    tiles.append(
                        business_tile.render_template_fragment(
                            result_context
                        )
                    )
                elif result.content_type.name == 'offer':
                    offer_tile = OfferTile()
                    result_context = Context({
                        'offer': result,
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

            except:
                logger.exception('SEARCH RESULT FROM HAYSTACK BLEW THE STACK - FIX - SERIOUSLY')

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

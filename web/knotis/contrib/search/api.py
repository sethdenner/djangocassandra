import copy
from django.utils.log import logging
logger = logging.getLogger(__name__)

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import APIException

from haystack.utils.geo import Point
from haystack.query import SearchQuerySet

from knotis.views import ApiViewSet

from knotis.contrib.identity.models import (
    IdentityEstablishment,
    IdentityTypes
)
from knotis.contrib.identity.mixins import GetCurrentIdentityMixin
from knotis.contrib.offer.models import Offer
from knotis.contrib.transaction.models import TransactionTypes

from .serializers import SearchSerializer


class SearchApi(object):
    @staticmethod
    def search(
        identity=None,
        **filters
    ):
        search_type = filters.pop('t', None)
        query_set = SearchQuerySet()

        if search_type == 'offer':
            model = Offer

        elif search_type == 'identity':
            model = IdentityEstablishment

        else:
            model = None

        if (
            identity is None or
            identity.identity_type != IdentityTypes.SUPERUSER
        ):
            filters['available'] = True

        filters.pop('format', None)

        latitude = filters.pop('lat', None)
        longitude = filters.pop('lon', None)

        if None is not model:
            query_set = query_set.models(model)

        else:  # This will most definitely have to change.
            query_set = query_set.models(Offer, IdentityEstablishment)

        query_set = query_set.filter(**filters)

        if latitude is not None and longitude is not None:
            current_location = Point(
                float(longitude),
                float(latitude)
            )

            query_set = query_set.distance(
                'location',
                current_location
            ).order_by('distance')

        return query_set

    @staticmethod
    def search_offers(
        identity=None,
        filters={}
    ):
        filters['t'] = 'offer'
        return SearchApi.search(
            identity,
            filters
        )

    @staticmethod
    def search_identities(
        identity=None,
        filters={}
    ):
        filters['t'] = 'identity'
        return SearchApi.search(
            identity,
            filters
        )

    @staticmethod
    def search_businesses(
        identity=None,
        filters={}
    ):
        filters['idtype'] = IdentityTypes.BUSINESS
        return SearchApi.search_identities(
            identity,
            filters
        )

    @staticmethod
    def search_establishments(
        identity=None,
        filters={}
    ):
        filters['idtype'] = IdentityTypes.ESTABLISHMENT
        return SearchApi.search_identities(
            identity,
            filters
        )

    @staticmethod
    def search_individuals(
        identity=None,
        filters={}
    ):
        filters['idtype'] = IdentityTypes.INDIVIDUAL
        return SearchApi.search_identities(
            identity,
            filters
        )

    @staticmethod
    def search_transactions(
        identity=None,
        filters={}
    ):
        filters['t'] = 'transaction'
        return SearchApi.search(
            identity,
            filters
        )

    @staticmethod
    def search_purchases(
        identity=None,
        filters={}
    ):
        filters['ttype'] = TransactionTypes.PURCHASE
        return SearchApi.search_transactions(
            identity,
            filters
        )

    @staticmethod
    def search_redemptions(
        identity=None,
        filters={}
    ):
        filters['ttype'] = TransactionTypes.REDEMPTION
        return SearchApi.search_transactions(
            identity,
            filters
        )


class InvalidRequest(APIException):
    status_code = 500
    default_detail = (
        'Service unable to handle request '
        'due to insufficient or invalid data.'
    )


class SearchApiViewSet(ApiViewSet, GetCurrentIdentityMixin):
    api_path = 'search'
    resource_name = 'search'

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def initial(
        self,
        request,
        *args,
        **kwargs
    ):
        super(SearchApiViewSet, self).initial(
            request,
            *args,
            **kwargs
        )

        self.get_current_identity(request)

    def list(
        self,
        request
    ):
        parameters = copy.copy(request.QUERY_PARAMS)
        search_query = parameters.pop('q', None)
        if None is search_query:
            raise InvalidRequest()

        if isinstance(search_query, list):
            search_query = ' '.join(search_query)

        filters = {
            key: value for (key, value) in parameters.iteritems()
        }
        filters['content'] = search_query

        results = SearchApi.search(
            identity=self.current_identity,
            **filters
        )

        data = []

        for result in results:
            serializer = SearchSerializer(instance=result, many=False)
            data.append(serializer.data.get('object'))

        return Response(data)

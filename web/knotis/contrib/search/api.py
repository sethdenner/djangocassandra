import copy
from django.utils.log import logging
logger = logging.getLogger(__name__)

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from haystack.query import SearchQuerySet

from knotis.views import ApiViewSet

from knotis.contrib.identity.models import (
    Identity,
    IdentityTypes
)
from knotis.contrib.offer.models import Offer
from knotis.contrib.transaction.models import TransactionTypes

from .serializers import SearchSerializer


class SearchApi(object):
    @staticmethod
    def search(
        search_query,
        identity=None,
        **filters
    ):
        search_type = filters.get('t')
        query_set = SearchQuerySet()

        if search_type == 'offer':
            model = Offer

        elif search_type == 'identity':
            model = Identity

        else:
            model = None

        if None is not model:
            query_set = query_set.models(model)

        results = query_set.filter(content=search_query)
        return results

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


from rest_framework.exceptions import APIException


class InvalidRequest(APIException):
    status_code = 500
    default_detail = (
        'Service unable to handle request '
        'due to insufficient or invalid data.'
    )


class SearchApiViewSet(ApiViewSet):
    api_path = 'search'
    resource_name = 'search'

    permission_classes = (IsAuthenticatedOrReadOnly,)

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

        identity_pk = parameters.pop('ci', None)
        if identity_pk:
            identity = Identity.objects.get(pk=identity_pk)

        else:
            identity = None

        filters = {
            key: value for (key, value) in request.QUERY_PARAMS.iteritems()
        }

        results = SearchApi.search(
            search_query,
            identity=identity,
            **filters
        )

        data = {}

        for result in results:
            serializer = SearchSerializer(instance=result, many=False)
            data.update(serializer.data)

        return Response(data)

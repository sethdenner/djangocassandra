from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView

class SearchApi(ApiView):
    api_url = 'search/'

from knotis.contrib.identity.views import EstablishmentsView


class IndexView(EstablishmentsView):
    url_patterns = [
        r'^[/]?$'
    ]

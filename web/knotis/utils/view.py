from BeautifulSoup import (
    BeautifulSoup,
    Comment
)

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.relation.models import Relation


valid_html_tags = 'p i strong b u a h1 h2 h3 pre br img'.split()
valid_html_attrs = 'href src'.split()


def sanitize_input_html(value):
    """
    Cleans non-allowed HTML from the input.

    http://djangosnippets.org/snippets/169/
    """
    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(
            text,
            Comment
        )
    ):
        comment.extract()

    for tag in soup.findAll(True):
        if tag.name not in valid_html_tags:
            tag.hidden = True

        tag.attrs = [
            (attr, val) for attr, val in tag.attrs if attr in valid_html_attrs
        ]

    return soup.renderContents().decode('utf8')


def get_boolean_from_request(
    request,
    key,
    method='POST'
):
    " gets the value from request and returns it's boolean state "
    value = getattr(request, method).get(key, False)

    if isinstance(value, basestring):
        value = value.lower()

    if not value or value == 'false' or value == '0':
        value = False
    elif value:
        value = True

    return value


def format_currency(value):
    return ("%.2f" % round(
        value,
        2
    )).replace('.00', '')

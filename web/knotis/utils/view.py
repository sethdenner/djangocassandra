from BeautifulSoup import (
    BeautifulSoup,
    Comment
)

from django.conf import settings

from knotis.contrib.auth.models import (
    KnotisUser,
    UserProfile,
)
from knotis.contrib.content.models import Content
from knotis.contrib.category.models import (
    City,
    Neighborhood,
)


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


def get_standard_template_parameters(request):
    template_parameters = {}

    template_parameters['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
    template_parameters['session'] = request.session
    template_parameters['settings'] = settings

    try:
        content = {}

        content_set = Content.objects.get_template_content('header')
        for c in content_set:
            content[c.name] = c.value

        content_set = Content.objects.get_template_content('footer')
        for c in content_set:
            content[c.name] = c.value

        template_parameters.update(content)

        template_parameters['cities'] = City.objects.all()
        template_parameters['neighborhoods'] = Neighborhood.objects.all()

        if request.user.is_authenticated():
            knotis_user = KnotisUser.objects.get(pk=request.user.id)
            template_parameters['knotis_user'] = knotis_user
            user_profile = UserProfile.objects.get(user=request.user)
            template_parameters['user_profile'] = user_profile
            template_parameters['username_truncated'] = \
                knotis_user.username_12()
            template_parameters['avatar_uri'] = knotis_user.avatar(
                request.session.get('fb_id')
            )

    except:
        pass

    return template_parameters


def format_currency(value):
    return ("%.2f" % round(
        value,
        2
    )).replace('.00', '')

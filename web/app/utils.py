import uuid
import datetime
import calendar

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from knotis_auth.models import KnotisUser, UserProfile

from app.models.contents import Content
from app.models.cities import City
from app.models.neighborhoods import Neighborhood


class Time:
    @staticmethod
    def add_months(sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)


class View:
    @staticmethod
    def get_boolean_from_request(request, key, method='POST'):
        " gets the value from request and returns it's boolean state "
        value = getattr(request, method).get(key, False)

        if isinstance(value, basestring):
            value = value.lower()

        if not value or value == 'false' or value == '0':
            value = False
        elif value:
            value = True

        return value

    @staticmethod
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

    @staticmethod
    def format_currency(value):
        return ("%.2f" % round(
            value,
            2
        )).replace('.00', '')


class Email:
    @staticmethod
    def generate_validation_key():
        key = uuid.uuid4().hex
        return "%s-%s-%s-%s-%s" % (
            key[:8],
            key[8:12],
            key[12:16],
            key[16:20],
            key[20:]
        )

    @staticmethod
    def generate_email(
        template,
        subject,
        from_email,
        recipients_list,
        data={}
    ):
        text = get_template('email/' + template + '.txt')
        html = get_template('email/' + template + '.html')

        context = Context(data)

        text_content = text.render(context)
        html_content = html.render(context)
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            recipients_list
        )
        email.attach_alternative(
            html_content,
            "text/html"
        )
        return email

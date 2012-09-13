import md5

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from app.models.contents import Content
from app.models.users import UserProfile


class View:

    @staticmethod
    def get_standard_template_parameters(request):
        template_parameters = {}

        template_parameters['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID

        try:
            content = {}

            content_set = Content.objects.get_template_content('header')
            for c in content_set:
                content[c.name] = c.value

            content_set = Content.objects.get_template_content('footer')
            for c in content_set:
                content[c.name] = c.value

            template_parameters.update(content)

            if request.user.is_authenticated():
                user_profile = UserProfile.objects.get(user=request.user)
                template_parameters['user_profile'] = user_profile
                template_parameters['username_truncated'] = request.user.username[:9] + '...'
                template_parameters['avatar_uri'] = User.get_avatar(
                    request.user.username,
                    None,
                    20
                )

        except:
            pass

        return template_parameters


class Email:

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


class User:

    @staticmethod
    def get_avatar(
        email,
        facebook_id=None,
        s=32,
        d='mm',
        r='g',
        img=False,
        img_attrs={}
    ):
        return Gravatar.get_avatar(
            email,
            s,
            d,
            r,
            img,
            img_attrs
        ) if not facebook_id else Facebook.get_avatar(facebook_id)


class Gravatar:

    @staticmethod
    def get_avatar(
        email,
        s=32,
        d='mm',
        r='g',
        img=False,
        img_attrs={}
    ):
        url = 'http://www.gravatar.com/avatar/'
        url += md5.new(email.lower().strip()).hexdigest()
        url += '?s=%i&d=%s&r=%s' % (s, d, r)

        if img:
            url = '<img src="' + url + '"'
            for key in img_attrs:
                url += ' ' + key + '="' + img_attrs[key] + '"'
            url += ' />'

        return url


class Facebook:

    @staticmethod
    def get_avatar(facebook_id):
        return None

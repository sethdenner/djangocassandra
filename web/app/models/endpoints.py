import md5
import random
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import CharField, DateTimeField, BooleanField, \
    IntegerField, Manager
from django.core.mail import send_mail, BadHeaderError
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
# from app.models.fields.permissions import PermissionsField


class EndpointManager(Manager):
    def create_endpoint(
        self,
        user,
        endpoint_type,
        value,
        primary=False,
        validation_key=None,
        disabled=False
    ):
        class_type = Endpoint
        if Endpoint.EndpointTypes.EMAIL == endpoint_type:
            class_type = EndpointEmail
        elif Endpoint.EndpointTypes.ADDRESS == endpoint_type:
            class_type = EndpointAddress
        elif Endpoint.EndpointTypes.PHONE == endpoint_type:
            class_type = EndpointPhone
        elif Endpoint.EndpointTypes.FACEBOOK == endpoint_type:
            class_type = EndpointFacebook
        elif Endpoint.EndpointTypes.TWITTER == endpoint_type:
            class_type = EndpointTwitter
        elif Endpoint.EndpointTypes.YELP == endpoint_type:
            class_type = EndpointYelp
        else:
            class_type = Endpoint

        endpoint = class_type(
            user=user,
            primary=primary,
            value=value,
            validation_key=validation_key,
            disabled=disabled
        )
        endpoint.save()

        return endpoint

    def validate_endpoints(
        self,
        validation_key,
        user=None,
        endpoints=[]
    ):
        if endpoints:
            endpoint_set = endpoints
        elif user:
            endpoint_set = self.filter(user=user)
        else:
            raise ValueError('Could not validate endpoint. user and endpoints both None.')

        for endpoint in endpoint_set:
            if endpoint.validation_key == validation_key:
                return endpoint.validate(validation_key)

        return False

class Endpoint(KnotisModel):
    class EndpointTypes:
        UNDEFINED = -1
        EMAIL = 0
        PHONE = 1
        ADDRESS = 2
        TWITTER = 3
        FACEBOOK = 4
        YELP = 5

        CHOICES = (
            (UNDEFINED, 'Undefined'),
            (EMAIL, 'Email'),
            (PHONE, 'Phone'),
            (ADDRESS, 'Address'),
            (TWITTER, 'Twitter'),
            (FACEBOOK, 'Facebook'),
            (YELP, 'Yelp')
        )

    type = IntegerField(choices=EndpointTypes.CHOICES, default=EndpointTypes.UNDEFINED)

    user = ForeignKeyNonRel(User)
    value = ForeignKeyNonRel(Content)

    primary = BooleanField(default=False)
    validated = BooleanField(default=False)
    validation_key = CharField(max_length=256, null=True, blank=True, default=None)
    disabled = BooleanField(default=False)

    pub_date = DateTimeField('date published', auto_now_add=True)

    objects = EndpointManager()

    def validate(
        self,
        validation_key
    ):
        if validation_key == self.validation_key:
            self.validated = True
            self.save()

        return self.validated

    @staticmethod
    def _value_string_to_content(kwargs):
        value = kwargs.get('value')

        if None == value or isinstance(value, Content):
            return

        if not isinstance(value, basestring):
            raise ValueError('value must be type <Content> or type <basestring>.')

        endpoint_type = kwargs.get('type')
        if endpoint_type == 0:
            content_type = '4.1'
        elif endpoint_type == 1:
            content_type = '4.2'
        elif endpoint_type == 2:
            content_type = '4.3'
        elif endpoint_type == 3:
            content_type = '4.4'
        elif endpoint_type == 4:
            content_type = '4.5'
        elif endpoint_type == 5:
            content_type = '4.6'
        else:
            content_type = '4.0'

        content = Content(
            content_type=content_type,
            user=kwargs.get('user'),
            name=value,
            value=value,
        )
        content.save()

        kwargs['value'] = content

    def send_message(self, **kwargs):
        raise NotImplementedError('send_message was not implemented in derived \
            class ' + self.__class__.__name__ + '.')


""" Endpoint Proxy Classes """
class EndpointPhone(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 1

        Endpoint._value_string_to_content(kwargs)

        super(EndpointPhone, self).__init__(*args, **kwargs)


class EndpointEmail(Endpoint): #-- the data for all these is the same, we want different actual
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 0  # Always override the type to email (0).

        Endpoint._value_string_to_content(kwargs)

        if kwargs.get('validation_key') is None:
            validation_hash = md5.new()

            validation_hash.update('%10.10f' % random.random())

            now = datetime.now()
            milliseconds = (now.day * 24 * 60 * 60 + now.second) * 1000 \
                + now.microsecond / 1000.0
            validation_hash.update('%i' % milliseconds)

            kwargs['validation_key'] = validation_hash.hexdigest()

        super(EndpointEmail, self).__init__(*args, **kwargs)

    def send_message(self, **kwargs):
        try:
            subject = kwargs.get('subject')
            message = kwargs.get('message')
            from_email = kwargs.get('from_address')
            recipient_list = kwargs.get('recipient_list')

            send_mail(
                subject,
                message,
                from_email,
                recipient_list
            )
        except BadHeaderError as e:
            pass
        except:
            pass


class EndpointTwitter(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 3

        Endpoint._value_string_to_content(kwargs)

        super(EndpointTwitter, self).__init__(*args, **kwargs)


class EndpointFacebook(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 4

        Endpoint._value_string_to_content(kwargs)

        super(EndpointFacebook, self).__init__(*args, **kwargs)


class EndpointYelp(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 5

        Endpoint._value_string_to_content(kwargs)

        super(EndpointYelp, self).__init__(*args, **kwargs)


class EndpointAddress(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 2

        Endpoint._value_string_to_content(kwargs)

        super(EndpointAddress, self).__init__(*args, **kwargs)

from django.db.models import (
    CharField,
    DateTimeField,
    BooleanField,
    IntegerField,
    Manager
)
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User

from knotis.utils.email import generate_validation_key
from knotis.contrib.core.models import KnotisModel
from knotis.contrib.content.models import Content, ContentTypes
from knotis.contrib.cassandra.models import ForeignKey


class EndpointManager(Manager):
    def create_endpoint(
        self,
        endpoint_type,
        value,
        user=None,
        primary=False,
        validation_key=None,
        disabled=False
    ):
        class_type = Endpoint
        if EndpointTypes.EMAIL == endpoint_type:
            class_type = EndpointEmail
        elif EndpointTypes.ADDRESS == endpoint_type:
            class_type = EndpointAddress
        elif EndpointTypes.PHONE == endpoint_type:
            class_type = EndpointPhone
        elif EndpointTypes.FACEBOOK == endpoint_type:
            class_type = EndpointFacebook
        elif EndpointTypes.TWITTER == endpoint_type:
            class_type = EndpointTwitter
        elif EndpointTypes.YELP == endpoint_type:
            class_type = EndpointYelp
        else:
            class_type = Endpoint

        endpoint = class_type.objects.create(
            user=user,
            primary=primary,
            value=value,
            validation_key=validation_key,
            disabled=disabled
        )

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
            raise ValueError(
                'Could not validate endpoint. user and endpoints both None.'
            )

        for endpoint in endpoint_set:
            if endpoint.validation_key == validation_key:
                return endpoint.validate(validation_key)

        return False


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


class Endpoint(KnotisModel):
    type = IntegerField(
        choices=EndpointTypes.CHOICES,
        default=EndpointTypes.UNDEFINED
    )

    user = ForeignKey(User)
    value = ForeignKey(Content)

    primary = BooleanField(default=False)
    validated = BooleanField(default=False)
    validation_key = CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None
    )
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

    def update(
        self,
        value=None,
        primary=None,
        disabled=None
    ):
        if None != value:
            current_value = self.value.value if self.value else None
            if value != current_value:
                if self.value:
                    self.value = self.value.update(value)
                else:
                    self.value = Content.objects.create(

                    )

                self.save()

    @staticmethod
    def _value_string_to_content(kwargs):
        value = kwargs.get('value')

        if None == value or isinstance(value, Content):
            return

        if not isinstance(value, basestring):
            raise ValueError('value must be type <Content> or type <basestring>.')

        endpoint_type = kwargs.get('type')
        if endpoint_type == EndpointTypes.EMAIL:
            content_type = ContentTypes.ENDPOINT_EMAIL
        elif endpoint_type == EndpointTypes.PHONE:
            content_type = ContentTypes.ENDPOINT_PHONE
        elif endpoint_type == EndpointTypes.ADDRESS:
            content_type = ContentTypes.ENDPOINT_ADDRESS
        elif endpoint_type == EndpointTypes.FACEBOOK:
            content_type = ContentTypes.ENDPOINT_FACEBOOK
        elif endpoint_type == EndpointTypes.TWITTER:
            content_type = ContentTypes.ENDPOINT_TWITTER
        elif endpoint_type == EndpointTypes.YELP:
            content_type = ContentTypes.ENDPOINT_YELP
        else:
            content_type = ContentTypes.ENDPOINT

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
        kwargs['type'] = EndpointTypes.EMAIL  # Always override the type to email (0).

        Endpoint._value_string_to_content(kwargs)

        if kwargs.get('validation_key') is None:
            kwargs['validation_key'] = generate_validation_key()

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
        kwargs['type'] = EndpointTypes.TWITTER

        Endpoint._value_string_to_content(kwargs)

        super(EndpointTwitter, self).__init__(*args, **kwargs)


class EndpointFacebook(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = EndpointTypes.FACEBOOK

        Endpoint._value_string_to_content(kwargs)

        super(EndpointFacebook, self).__init__(*args, **kwargs)


class EndpointYelp(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = EndpointTypes.YELP

        Endpoint._value_string_to_content(kwargs)

        super(EndpointYelp, self).__init__(*args, **kwargs)


class EndpointAddress(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['type'] = EndpointTypes.ADDRESS

        Endpoint._value_string_to_content(kwargs)

        super(EndpointAddress, self).__init__(*args, **kwargs)

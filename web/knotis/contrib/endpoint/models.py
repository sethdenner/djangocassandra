from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickUUIDField,
    QuickForeignKey,
    QuickGenericForeignKey,
    QuickBooleanField
)

from django.db.models import (
    CharField,
    DateTimeField,
    BooleanField,
    IntegerField,
    Manager
)
from django.core.mail import send_mail, BadHeaderError
from django.contrib.contenttypes.models import ContentType

from knotis.utils.email import generate_validation_key
from knotis.contrib.cassandra.models import ForeignKey
from knotis.contrib.identity.models import Identity


class EndpointManager(Manager):
    def create(
        self,
        *args,
        **kwargs
    ):
        if 'endpoint_type' in kwargs:
            endpoint_type = kwargs.get('endpoint_type')

        elif len(args):
            endpoint_type = args[0]

        else:
            endpoint_type = EndpointTypes.UNDEFINED

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

        endpoint = class_type(**kwargs)
        endpoint.save()

        return endpoint


    def validate_endpoints(
        self,
        validation_key,
        identity=None,
        endpoints=[]
    ):
        if endpoints:
            endpoint_set = endpoints
        elif identity:
            endpoint_set = self.filter(identity=identity)
        else:
            raise ValueError(
                'Could not validate endpoint. identity and '
                'endpoints both None.'
            )

        for endpoint in endpoint_set:
            if endpoint.validation_key == validation_key:
                return endpoint.validate(validation_key)

        return False

    def get_primary_endpoint(
        self,
        identity,
        endpoint_type
    ):
        endpoints = Endpoint.objects.filter(
            endpoint_type=endpoint_type,
            identity=identity
        )

        for endpoint in endpoints:
            if endpoint.primary:
                return endpoint

        return None



class EndpointTypes:
    UNDEFINED = -1
    EMAIL = 0
    PHONE = 1
    ADDRESS = 2
    TWITTER = 3
    FACEBOOK = 4
    YELP = 5
    IDENTITY = 6
    WIDGET = 7
    FOLLOWERS = 8

    CHOICES = (
        (UNDEFINED, 'Undefined'),
        (EMAIL, 'Email'),
        (PHONE, 'Phone'),
        (ADDRESS, 'Address'),
        (TWITTER, 'Twitter'),
        (FACEBOOK, 'Facebook'),
        (YELP, 'Yelp'),
        (IDENTITY, 'Identity'),
        (WIDGET, 'Widget'),
        (FOLLOWERS, 'Followers')
    )


class Endpoint(QuickModel):
    endpoint_type = IntegerField(
        choices=EndpointTypes.CHOICES,
        default=EndpointTypes.UNDEFINED,
        db_index=True
    )

    identity = ForeignKey(Identity)
    value = CharField(
        max_length=256,
        db_index=True
    )

    primary = BooleanField(default=False)
    validated = BooleanField(default=False)
    validation_key = CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None
    )
    disabled = BooleanField(default=False)

    objects = EndpointManager()

    def save(
        self,
        *args,
        **kwargs
    ):
        super(Endpoint, self).save(*args, **kwargs)

        endpoints = Endpoint.objects.filter(
            identity=self.identity,
            endpoint_type=self.endpoint_type,
            primary=True
        )

        if self.primary:
            for endpoint in endpoints:
                if endpoint.id != self.id:
                    endpoint.primary = False
                    endpoint.save()

    def validate(
        self,
        validation_key
    ):
        if validation_key == self.validation_key:
            self.validated = True
            self.save()

        return self.validated

    def send_message(self, **kwargs):
        raise NotImplementedError(
            'send_message was not implemented in derived class ' +
            self.__class__.__name__ + '.'
        )


class EndpointPhone(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.PHONE

        super(EndpointPhone, self).__init__(*args, **kwargs)


class EndpointEmail(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        # Always override the type to email (0).
        kwargs['endpoint_type'] = EndpointTypes.EMAIL

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

        except BadHeaderError:
            pass

        except:
            pass


class EndpointTwitter(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.TWITTER

        super(EndpointTwitter, self).__init__(*args, **kwargs)


class EndpointFacebook(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.FACEBOOK

        super(EndpointFacebook, self).__init__(*args, **kwargs)


class EndpointYelp(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.YELP

        super(EndpointYelp, self).__init__(*args, **kwargs)


class EndpointAddress(Endpoint):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.ADDRESS

        super(EndpointAddress, self).__init__(*args, **kwargs)


class EndpointIdentityManager(EndpointManager):
    def update_identity_endpoints(
        self,
        identity
    ):
        if not hasattr(identity, 'endpoint_set'):
            return

        identity_endpoints = identity.endpoint_set.filter(
            endpoint_type=EndpointTypes.IDENTITY
        )

        for e in identity_endpoints:
            e.value = identity.name
            e.save()


class EndpointIdentity(Endpoint):
    class Meta:
        proxy = True

    objects = EndpointIdentityManager()

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.IDENTITY

        super(EndpointIdentity, self).__init__(*args, **kwargs)

    def update_value(self):
        self.value = self.identity.name
        self.save()


class Publish(QuickModel):
    endpoint = QuickForeignKey(Endpoint)
    subject_content_type = QuickForeignKey(
        ContentType,
        related_name='publish_subject_set'
    )
    subject_object_id = QuickUUIDField()
    subject = QuickGenericForeignKey(
        'subject_content_type',
        'subject_object_id'
    )

    publish_now = QuickBooleanField(
        db_index=True,
        default=True
    )

    completed = QuickBooleanField(
        db_index=True,
        default=False
    )

    def publish(self):
        raise NotImplementedError(
            'publish was not implemented in derived class ' +
            self.__class__.__name__ + '.'
        )

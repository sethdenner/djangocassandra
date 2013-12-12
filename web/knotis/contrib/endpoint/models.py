from knotis.contrib.quick.models import (
    QuickModel,
    QuickManager
)
from knotis.contrib.quick.fields import (
    QuickUUIDField,
    QuickForeignKey,
    QuickGenericForeignKey,
    QuickBooleanField
)

from django.db.models import (
    CharField,
    BooleanField,
    IntegerField,
    Manager
)
from django.core.mail import send_mail, BadHeaderError
from django.contrib.contenttypes.models import ContentType

from knotis.utils.email import generate_validation_key
from knotis.contrib.cassandra.models import ForeignKey
from knotis.contrib.identity.models import Identity


def normalize_arguments(*args, **kwargs):
    for key in kwargs.keys():
        if not kwargs[key]:
            del kwargs[key]


class EndpointManager(QuickManager):
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

        elif EndpointTypes.WEBSITE == endpoint_type:
            class_type = EndpointWebsite

        else:
            class_type = Endpoint

        endpoint = class_type(**kwargs)
        endpoint.clean()
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

    def _get_endpoint_class(self, endpoint_type):
        class_names = dict(
            (key, 'Endpoint' + name) for (key, name) in EndpointTypes.CHOICES
        )
        return globals()[class_names[endpoint_type]]

    def get_primary_endpoint(
        self,
        identity,
        endpoint_type
    ):

        EndpointClass = self._get_endpoint_class(endpoint_type)

        endpoints = EndpointClass.objects.filter(
            endpoint_type=endpoint_type,
            identity=identity
        )

        for endpoint in endpoints:
            if endpoint.primary:
                return endpoint

        return None

    def update_or_create(
        self,
        *args,
        **kwargs
    ):
        endpoint_class_dict = {
            EndpointTypes.TWITTER: EndpointTwitter,
            EndpointTypes.YELP: EndpointYelp,
            EndpointTypes.EMAIL: EndpointEmail,
            EndpointTypes.WEBSITE: EndpointWebsite,
            EndpointTypes.PHONE: EndpointPhone,
            EndpointTypes.FACEBOOK: EndpointFacebook
        }

        if 'endpoint_type' in kwargs.keys():
            endpoint_class = endpoint_class_dict[kwargs['endpoint_type']]
        else:
            raise Exception('No EndpointType specified')

        # create a new filter including only filterable fields
        filterable_fields = endpoint_class.get_filterable_fields()

        filter_parameters = {
            key: kwargs[key] for key in filterable_fields
            if key in kwargs.keys() and kwargs[key] != ''
        }

        # see if there are any endpoints under this filter
        # endpoints = endpoint_class.objects.filter(**filter_parameters)
        endpoints = Endpoint.objects.filter(**filter_parameters)
        endpoints = endpoints.select_subclasses()

        if len(endpoints) > 1:
            raise Exception('Too many endpoints match query')

        # if there are not, remove pk from filter so it doesn't get overidden
        elif len(endpoints) == 0:
            if 'pk' in filter_parameters.keys():
                del filter_parameters['pk']
            endpoint = endpoint_class.objects.create(**filter_parameters)

        # if there are, use the first retrieved endpoint for the nex step
        else:
            endpoint = endpoints[0]

            # update the endpoint
            for attr in filter_parameters.keys():
                setattr(endpoint, attr, filter_parameters[attr])
                
            endpoint.clean()

            params = filter_parameters
            if 'value' not in params.keys() or params['value'].strip() == '':
                endpoint.deleted = True
                endpoint.delete()
                            
            endpoint.save()

        return endpoint


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
    WEBSITE = 9
    LINK = 10

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
        (FOLLOWERS, 'Followers'),
        (WEBSITE, 'Website'),
        (LINK, 'Link')
    )

    SubTypes = {}

    def register(endpoint_class):
        EndpointTypes.SubTypes[endpoint_class.EndpointType] = endpoint_class


EndpointTypeNames = {key: value for key, value in EndpointTypes.CHOICES}


class Endpoint(QuickModel):
    EndpointType = EndpointTypes.UNDEFINED

    endpoint_type = IntegerField(
        choices=EndpointTypes.CHOICES,
        default=EndpointTypes.UNDEFINED,
        db_index=True,
        blank=False
    )

    identity = ForeignKey(Identity)
    value = CharField(
        max_length=256,
        db_index=True,
        blank=False
    )
    context = CharField(
        max_length=256,
        db_index=True,
        blank=False
    )

    primary = BooleanField(
        default=False,
        db_index=True
    )
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

    def get_uri(self):
        return self.value
    
    def prepend_http(self, string):
        if string.strip().startswith('http'):
            return string
        else:
            return 'http://' + self.value.strip()


class EndpointPhone(Endpoint):
    EndpointType = EndpointTypes.PHONE

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.PHONE

        super(EndpointPhone, self).__init__(*args, **kwargs)

    def get_uri(self):
        return "callto:" + self.value

    
class EndpointEmail(Endpoint):
    EndpointType = EndpointTypes.EMAIL

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

    def get_uri(self):
        return "mailto:" + self.value

    
class EndpointTwitter(Endpoint):
    EndpointType = EndpointTypes.TWITTER
    
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.TWITTER

        super(EndpointTwitter, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Set value as the twitter handle only.

        Strip off twitter.com if it's there ad it back in get_uri
        """
        v = self.value.strip()

        if v.split('/', 1)[0].find('.'):  # is absolute
            prefixes = [
                'twitter.com/',
                'http://twitter.com/',
                'www.twitter.com/',
                'http://www.twitter.com/'
            ]
            for prefix in prefixes:
                if v[:len(prefix)] == prefix:
                    self.value = self.value[len(prefix):]
                    break
        
        super(Endpoint, self).clean()

    def get_uri(self):
        return "http://twitter.com/" + self.value

    
class EndpointFacebook(Endpoint):
    EndpointType = EndpointTypes.FACEBOOK

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.FACEBOOK

        super(EndpointFacebook, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Set value as the facebook username only.

        Strip off facebook.com (and its derivatives) if it's there add it
        back in get_uri
        """
        v = self.value.strip()

        if v.split('/', 1)[0].find('.'):  # is absolute
            prefixes = [
                'facebook.com/',
                'http://facebook.com/',
                'www.facebook.com/',
                'http://www.facebook.com/',
                
                'facebook.com/profile.php?id=',
                'http://facebook.com/profile.php?id=',
                'www.facebook.com/profile.php?id=',
                'http://www.facebook.com/profile.php?id=',
            ]
            for prefix in prefixes:
                if (len(v) > len(prefix)) and (v[:len(prefix)] == prefix):
                    self.value = self.value[len(prefix):]
                    break
        
        super(Endpoint, self).clean()

    def get_uri(self):
        return "http://facebook.com/profile.php?id=" + self.value

    
class EndpointYelp(Endpoint):
    EndpointType = EndpointTypes.YELP
    
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.YELP

        super(EndpointYelp, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Set value as the yelp handle only.

        Strip off yelp.com and derivatives if it's there ad it back in get_uri
        """
        v = self.value.strip()

        if v.split('/', 1)[0].find('.'):  # is absolute
            prefixes = [
                'yelp.com/',
                'http://yelp.com/',
                'www.yelp.com/',
                'http://www.yelp.com/'
            ]
            for prefix in prefixes:
                if v[:len(prefix)] == prefix:
                    self.value = self.value[len(prefix):]
                    break
        
        super(Endpoint, self).clean()

    def get_uri(self):
        return "http://yelp.com/biz/" + self.value


class EndpointAddress(Endpoint):
    EndpointType = EndpointTypes.ADDRESS

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.ADDRESS

        super(EndpointAddress, self).__init__(*args, **kwargs)

        
class EndpointLink(Endpoint):
    EndpointType = EndpointTypes.LINK

    class Meta:
        proxy = True

    def clean(self):
        """
        Check that the value has http or https if it contains a domain.
        If it contains a domain and no protocol, add http:// to the beginning.
        """
        v = self.value.strip()
        """ If the text before the first / contains a ., the url needs http """
        is_global = v.split('/', 1)[0].find('.') > 0
        if is_global:
            self.prepend_http(self.value)
                
        super(EndpointLink, self).clean()

    def get_uri(self):
        return self.value

    def get_display(self):
        """ 
        strip off http://, etc. for display
        """
        prefix = 'http://'
        if self.value[:len(prefix)] == prefix:
            return self.value[len(prefix):]
        prefix = 'https://'
        if self.value[:len(prefix)] == prefix:
            return self.value[len(prefix):]
        return self.value
            
        
class EndpointWebsite(EndpointLink):
    EndpointType = EndpointTypes.WEBSITE

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.WEBSITE

        super(EndpointWebsite, self).__init__(*args, **kwargs)

    def get_uri(self):
        return self.prepend_http(self.value)

        
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
    EndpointType = EndpointTypes.IDENTITY

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


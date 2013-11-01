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

from knotis.contrib.identity.models import (
    IdentityBusiness,
    IdentityTypes
)

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

        elif EndpointTypes.WEBSITE == endpoint_type:
            class_type = EndpointWebsite

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

    def _get_endpoint_class(self, endpoint_type):
        class_names = dict((key, 'Endpoint' + name) for (key, name) in EndpointTypes.CHOICES)
        return globals()[class_names[endpoint_type]]


    def get_primary_endpoint(
        self,
        identity,
        endpoint_type
    ):

        EndpointClass = self._get_endpoint_class(endpoint_type)

        endpoints = EndpointClass.objects.filter(
            endpoint_type=endpoint_type,
            identity=IdentityBusiness.objects.identity_id_to_business(identity.pk)
        )

        for endpoint in endpoints:
            if endpoint.primary:
                return endpoint

        return None


class EndpointTypes:
    UNDEFINED  = -1
    EMAIL      = 0
    PHONE      = 1
    ADDRESS    = 2
    TWITTER    = 3
    FACEBOOK   = 4
    YELP       = 5
    IDENTITY   = 6
    WIDGET     = 7
    FOLLOWERS  = 8
    WEBSITE    = 9
    LINK       = 10
    
    CHOICES = (
        (UNDEFINED,  'Undefined'),
        (EMAIL,      'Email'),
        (PHONE,      'Phone'),
        (ADDRESS,    'Address'),
        (TWITTER,    'Twitter'),
        (FACEBOOK,   'Facebook'),
        (YELP,       'Yelp'),
        (IDENTITY,   'Identity'),
        (WIDGET,     'Widget'),
        (FOLLOWERS,  'Followers'),
        (WEBSITE,    'Website'),
        (LINK,       'Link')
    )

    SubTypes = {}
    def register(endpoint_class):
        SubTypes[endpoint_class.EndpointType] = endpoint_class

class Endpoint(QuickModel):
    EndpointType = EndpointTypes.UNDEFINED
    

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
    context = CharField(
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

    def get_uri(self):
        return self.value


    def update_or_create(
        self,
        *args,
        **kwargs
    ):
        
        endpoints = Endpoint.objects.filter(**kwargs)
        if len(endpoints) > 1:
            raise Exception('Too many endpoints match query')
            
        elif len(endpoints) == 0:
            endpoint = Endpoint.objects.create(**kwargs)
        
        else:
            endpoint = endpoints[0]
            for attr in kwargs.keys():
                setattr(endpoint, attr, kwargs[attr])

        endpoint.save()
        return endpoint
        

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

        if v.split('/',1)[0].find('.'): # is absolute
            prefixes = ['twitter.com/', 'http://twitter.com/', 'www.twitter.com/', 'http://www.twitter.com/']
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

        Strip off facebook.com (and its derivatives) if it's there ad it back in get_uri
        """
        v = self.value.strip()

        if v.split('/',1)[0].find('.'): # is absolute
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

        if v.split('/',1)[0].find('.'): # is absolute
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
        is_global = v.split('/',1)[0].find('.') > 0
        if is_global: 
            if v[:7] != 'http://' and v[:8] != 'https://':
                self.value = 'http://' + self.value
        
        super(EndpointLink, self).clean()

    def get_uri(self):
        return self.value

class EndpointWebsite(EndpointLink):
    EndpointType = EndpointTypes.WEBSITE
    

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['endpoint_type'] = EndpointTypes.WEBSITE

        super(EndpointWebsite, self).__init__(*args, **kwargs)


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


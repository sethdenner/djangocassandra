import md5
import random
from datetime import datetime

from django.contrib.auth.models import User, Group
from django.db.models import CharField, DateTimeField, BooleanField, \
    IntegerField
from django.core.mail import send_mail, BadHeaderError
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
# from app.models.fields.permissions import PermissionsField

class EndpointPermissionsType(KnotisModel):
    ENDPOINT_PERMISSION_TYPES = (
        ('0', 'promotions'),
        ('1', 'following'),
        ('2', 'best deals')
    )
    value = CharField(max_length=30, choices=ENDPOINT_PERMISSION_TYPES)
    created_by = CharField(max_length=1024)
    pub_date = DateTimeField('date published')

class Endpoint(KnotisModel):
    ENDPOINT_TYPES = (
        ('0', 'email'),
        ('1', 'phone')
    )

    type = IntegerField(choices=ENDPOINT_TYPES)
    
    user = ForeignKeyNonRel(User, primary_key=True)
    value = ForeignKeyNonRel(Content)

    primary = BooleanField(default=False)
    validated = BooleanField(default=False)
    validation_key = CharField(max_length=256, null=True, blank=True)
    disabled = BooleanField(default=False)

    pub_date = DateTimeField('date published', auto_now_add=True)
    
    def send_message(self, **kwargs):
        raise NotImplementedError('send_message was not implemented in derived \
            class ' + self.__class__.__name__ + '.')
    

class EndpointPermissions(KnotisModel):
    endpoint = ForeignKeyNonRel(Endpoint)
    endpoint_permission_type = ForeignKeyNonRel(EndpointPermissionsType)


""" Endpoint Proxy Classes """
class EndpointPhone(Endpoint):
    class Meta:
        proxy = True

    def send_message(self, **kwargs):
        pass


class EndpointEmail(Endpoint): #-- the data for all these is the same, we want different actual
    class Meta:
        proxy = True
        
    def __init__(self, *args, **kwargs):
        kwargs['type'] = 0  # Always override the type to email (0).
        
        value = kwargs.get('value')
        if value and not isinstance(value, Content):
            content = None
            if isinstance(value, basestring):
                content = Content(
                    content_type='4.1',
                    locale='en_us',
                    user=kwargs.get('user'),
                    group=None,
                    parent=None,
                    previous=None,
                    value=value,
                    certainty_mu=1.,
                    certainty_sigma=0.
                )
                content.save() 
            else:
                raise ValueError('value must be type <Content> or type <str>.')
            
            kwargs['value'] = content
        
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

    def send_message(self, **kwargs):
        pass


class EndpointSMS(Endpoint):
    class Meta:
        proxy = True

    def send_message(self, **kwargs):
        pass


class EndpointAddress(Endpoint):
    class Meta:
        proxy = True

    def send_message(self, **kwargs):
        pass

#    street = CharField(max_length=1024)
#    street_2 = CharField(max_length=1024)
#    street_3 = CharField(max_length=1024)
#    city = CharField(max_length=1024)
#    state = CharField(max_length=1024)
#    zipcode = CharField(max_length=1024)
#    country = CharField(max_length=1024)
#
#    def send_message(self):
#        pass

#class EndpointInternationalAddress(Endpoint):


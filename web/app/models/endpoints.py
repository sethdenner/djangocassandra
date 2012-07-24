from django.contrib.auth.models import User, Group
from django.db.models import CharField, DateTimeField, BooleanField, ManyToManyField
from foreignkeynonrel.models import ForeignKeyNonRel
from app.models.knotis import KnotisModel
from app.models.contents import Content
from app.models.fields.permissions import PermissionsField

class EndpointType(KnotisModel):
    ENDPOINT_TYPES = (
        ('0', 'email'),
        ('1', 'phone')
    )

    value = CharField(max_length=30, choices=ENDPOINT_TYPES)
    created_by = CharField(max_length=1024)
    pub_date = DateTimeField('date published')

    def __unicode__(self):
        output_array = [
            self.value,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])

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
    endpoint_type = ForeignKeyNonRel(EndpointType)

    user = ForeignKeyNonRel(User)
    group = ForeignKeyNonRel(Group, null=True)
    #permissions = PermissionsField()
    content = ForeignKeyNonRel(Content)

    value = CharField(max_length=1024)
    validated = BooleanField(default=False)
    disabled = BooleanField(default=False)

    pub_date = DateTimeField('date published')

class EndpointPermissions(KnotisModel):
    endpoint = ForeignKeyNonRel(Endpoint)
    endpoint_permission_type = ForeignKeyNonRel(EndpointPermissionsType)

""" Endpoint Proxy Classes """
class EndpointEmail(Endpoint): #-- the data for all these is the same, we want different actual
    class Meta:
        proxy = True
    def send_message(self):
        pass

class EndpointTwitter(Endpoint):
    class Meta:
        proxy = True
    def send_message(self):
        pass

class EndpointSMS(Endpoint):
    class Meta:
        proxy = True
    def send_message(self):
        pass

class EndpointEmail(Endpoint):
    class Meta:
        proxy = True
    def send_message(self):
        pass

#class EndpointAddress(Endpoint):
#    #class Meta:
#    #    proxy = True
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


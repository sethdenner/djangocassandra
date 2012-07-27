from django.contrib.auth.models import User
from django.db.models import CharField, DateTimeField, FloatField, IntegerField
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel
from app.models.businesses import Business
from app.models.contents import Content
from app.models.endpoints import Endpoint, EndpointAddress, EndpointEmail, EndpointPhone
from app.models.fields.hours import HoursField
from manytomanynonrel.models import ManyToManyFieldNonRel


class Establishment(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Establishment"
        verbose_name_plural = 'Establishments'

    business = ForeignKeyNonRel(Business)

    content = ForeignKeyNonRel(Content)
    # this content node, has children for: Hours, Address, etc. about the business.
    # the piston api will need to be modified to return the correct content for each of these attributes.

    pub_date = DateTimeField('date published', auto_now_add=True)

    hours = ForeignKeyNonRel(Content, related_name='establishment_hours', null=True, blank=True)

    # endpoints = ManyToManyFieldNonRel(Endpoint, queryset=Endpoint.objects.all())

    address = ForeignKeyNonRel(EndpointAddress, related_name='establishment_address', null=True, blank=True)
    phone = ForeignKeyNonRel(EndpointPhone, related_name='establishment_phone', null=True, blank=True)
    email = ForeignKeyNonRel(EndpointEmail, related_name='establishment_email', null=True, blank=True)

    def __unicode__(self):
        output_array = [
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])


class EstablishmentEndpoint(KnotisModel):
    establishment = ForeignKeyNonRel(Establishment)
    endpoint = ForeignKeyNonRel(Endpoint)


class EstablishmentHours(KnotisModel):
    establishment = ForeignKeyNonRel(Establishment)
    hours = HoursField()
    order = IntegerField()

    def __unicode__(self):
        output_array = [
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])

#class EstablishmentHoursDaily(EstablishmentHours):
#    class Meta:
#        proxy = True
#    def __unicode__(self):
#        "Mon - Fri 9 to 5"
#
#class EstablishmentHoursAnually(EstablishmentHours):
#    class Meta:
#        proxy = True
#    def __unicode__(self):
#        "Closed Christmas"
#
#class EstablishmentHoursCalculatableHolidays(EstablishmentHours):
#
#class EstablishmentHoursSpecialOverrides(EstablishmentHours):

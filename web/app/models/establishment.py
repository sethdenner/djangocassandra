from django.db import models
from web.app.knotis.db import KnotisModel

from django.contrib.auth.models import User
from contents import Content
#from django.contrib.auth.models import User

class EstablishmentEndpoinst(KnotisModel):
    establishment = models.ForeignKey(Establishment)
    endpoint = models.ForeignKey(Endpoint)

class EstablishmentHours(KnotisModel):
    establishment = models.ForeignKey(Establishment)
    hours = models.HoursField("hours - fix me.")
    order = models.IntegerField()
        
class Establishment(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Establishment"
        verbose_name_plural = 'Establishments'
    
    business = models.ForeignKey(Business)

    content = models.ForeignKey(Content)
    # this content node, has children for: Hours, Address, etc. about the business.
    # the piston api will need to be modified to return the correct content for each of these attributes.

    pub_date = models.DateTimeField('date published')



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

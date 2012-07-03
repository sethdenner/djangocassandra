from django.db.models import CharField, ForeignKey, DateTimeField, FloatField

from app.models.knotis import KnotisModel

from contents import Content

"""
What is a product?  It's something that people engauge in economic activity to trade.  Sometimes it's a physical good, sometimes a service, sometimes an idea and sometimes it's a collection of other products grouped together.

This might be a bit too general.

Can these be ContentTypes?
    Description
    Reviews
    SKU
    tags
"""

# this isn't ready at all..
class Product(KnotisModel):
     content = ForeignKey('self')
     pub_date = DateTimeField('date published')

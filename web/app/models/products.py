from django.db.models import CharField, DateTimeField, FloatField
from foreignkeynonrel.models import ForeignKeyNonRel

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
    class Meta(KnotisModel.Meta):
        verbose_name = "Product"
        verbose_name_plural = 'Products'

    content_root = ForeignKeyNonRel(Content, related_name='product_content_root', null=True)
    # content = ManyToManyModelField(ForeignKeyNonRel(Content))
    name = CharField(max_length=140)

    # can be a url or maybe an id for gravatar.
    photo = ForeignKeyNonRel(Content, related_name='product_photo', null=True, blank=True)
    sku = ForeignKeyNonRel(Content, related_name='product_sku', null=True, blank=True)
    title = ForeignKeyNonRel(Content, related_name='product_title', null=True)
    description = ForeignKeyNonRel(Content, related_name='product_description', null=True)
    reviews_root = ForeignKeyNonRel(Content, related_name='product_reviews_root', null=True)

    # avatar = CharField(max_length=140, null=True)

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __unicode__(self):
        output_array = [
            self.name,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])

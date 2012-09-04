from django.db.models import ImageField

from knotis import KnotisModel
from contents import Content
from foreignkeynonrel.models import ForeignKeyNonRel

class Image(KnotisModel):
    image = ImageField(upload_to='/upload/images/')
    caption = ForeignKeyNonRel(Content, related_name='image_caption')

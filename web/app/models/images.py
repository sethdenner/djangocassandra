from sorl.thumbnail import ImageField

from knotis import KnotisModel
from contents import Content
from foreignkeynonrel.models import ForeignKeyNonRel

class Image(KnotisModel):
    image = ImageField(upload_to='offer/')
    caption = ForeignKeyNonRel(Content, related_name='image_caption', default=None)

from django.db.models import CharField
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField

from knotis import KnotisModel
from contents import Content
from foreignkeynonrel.models import ForeignKeyNonRel


class Image(KnotisModel):
    user = ForeignKeyNonRel(User)
    related_object_id = CharField(max_length=36, null=True, blank=True, default=None, db_index=True)
    image = ImageField(upload_to='images/')
    caption = ForeignKeyNonRel(Content, related_name='image_caption', default=None)

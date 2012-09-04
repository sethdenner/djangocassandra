from django.db.models import Manager
from django.utils.http import urlquote

from knotis import KnotisModel
from contents import Content
from foreignkeynonrel.models import ForeignKeyNonRel

class CityManager(Manager):
    def create_category(
        self,
        user,
        name
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))

        content_root = Content(
            content_type='6.0',
            user=user,
            name=backend_name
        )
        content_root.save()

        content_name = Content(
            content_type='6.1',
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )
        content_name.save()

        category = City(name=content_name)
        category.save()


class City(KnotisModel):
    name = ForeignKeyNonRel(Content, related_name='city_name')

    objects = CityManager()

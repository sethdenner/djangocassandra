from django.db.models import Manager
from django.utils.http import urlquote

from knotis import KnotisModel
from contents import Content, ContentTypes
from foreignkeynonrel.models import ForeignKeyNonRel

class CityManager(Manager):
    def create_city(
        self,
        user,
        name
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))

        content_root = Content.objects.create(
            content_type=ContentTypes.CITY,
            user=user,
            name=backend_name
        )

        content_name = Content.objects.create(
            content_type=ContentTypes.CITY_NAME,
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )

        return City.objects.create(
            content_root=content_root,
            name=content_name
        )


class City(KnotisModel):
    content_root = ForeignKeyNonRel(Content, related_name='city_root')
    name = ForeignKeyNonRel(Content, related_name='city_name')

    objects = CityManager()

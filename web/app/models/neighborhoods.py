from django.db.models import Manager
from django.utils.http import urlquote

from knotis import KnotisModel
from contents import Content, ContentTypes
from cities import City
from foreignkeynonrel.models import ForeignKeyNonRel

class NeighborhoodManager(Manager):
    def create_neighborhood(
        self,
        user,
        city,
        name
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))

        content_root = Content.objects.create(
            content_type=ContentTypes.NEIGHBORHOOD,
            user=user,
            name=backend_name
        )

        content_name = Content.objects.create(
            content_type=ContentTypes.NEIGHBORHOOD_NAME,
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )

        return Neighborhood.objects.create(
            content_root=content_root,
            name=content_name,
            city=city
        )


class Neighborhood(KnotisModel):
    content_root = ForeignKeyNonRel(Content, related_name='neighborhood_root')
    name = ForeignKeyNonRel(Content, related_name='neighborhood_name')
    city = ForeignKeyNonRel(City)

    objects = NeighborhoodManager()

from django.db.models import CharField, IntegerField, Manager
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
            name=content_name,
            name_denormalized=name
        )


class City(KnotisModel):
    content_root = ForeignKeyNonRel(Content, related_name='city_root')
    name = ForeignKeyNonRel(Content, related_name='city_name')
    name_denormalized = CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    active_offer_count = IntegerField(null=True, blank=True, default=0)

    objects = CityManager()

    def get_name(self):
        if None == self.name_denormalized:
            self.name_denormalized = self.name.value
            self.save()

        return self.name_denormalized

    def update(
        self,
        name
    ):
        is_self_dirty = False

        if None != name:
            current_name = self.name_denormalized if \
                self.name_denormalized else self.name.value
            if current_name != name:
                try:
                    self.name.update(name)
                    self.name_denormalized = name
                    is_self_dirty = True
                except:
                    pass

        if is_self_dirty:
            self.save()

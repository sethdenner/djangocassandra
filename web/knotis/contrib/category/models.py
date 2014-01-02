from django.db.models import CharField, IntegerField, Manager
from django.utils.http import urlquote

from knotis.contrib.core.models import KnotisModel
from knotis.contrib.content.models import Content, ContentTypes
from knotis.contrib.cassandra.models import ForeignKey


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
    content_root = ForeignKey(Content, related_name='city_root')
    name = ForeignKey(Content, related_name='city_name')
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


class CategoryManager(Manager):
    def create_category(
        self,
        user,
        name
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))

        content_root = Content.objects.create(
            content_type=ContentTypes.CATEGORY,
            user=user,
            name=backend_name
        )

        content_name = Content.objects.create(
            content_type=ContentTypes.CATEGORY_NAME,
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )

        return Category.objects.create(
            content_root=content_root,
            name=content_name,
            name_short=backend_name[:3]
        )


class Category(KnotisModel):
    content_root = ForeignKey(
        Content,
        related_name='category_root'
    )
    name = ForeignKey(
        Content,
        related_name='category_name'
    )
    name_short = CharField(
        max_length=3,
        null=True,
        blank=True,
        default=None,
        db_index=True
    )
    active_offer_count = IntegerField(
        null=True,
        blank=True,
        default=0
    )

    objects = CategoryManager()

    def short_name(self):
        return self.name_short

    def name_css(self):
        return self.name_short.title()

    def update(
        self,
        name=None
    ):
        is_self_dirty = False

        if None != name:
            current_name = self.name.value if self.name else None
            if name != current_name:
                if self.name:
                    self.name.update(name)

                else:
                    backend_name = urlquote(name.strip().lower().replace(
                        ' ',
                        '-'
                    ))

                    self.name = Content.objects.create(
                        content_type=ContentTypes.CATEGORY_NAME,
                        user=None,
                        name=backend_name + '_name',
                        parent=self.content_root,
                        value=name
                    )

                self.name_short = name.lower()[:3]
                is_self_dirty = True

        if is_self_dirty:
            self.save()


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
    content_root = ForeignKey(Content, related_name='neighborhood_root')
    name = ForeignKey(Content, related_name='neighborhood_name')
    city = ForeignKey(City)
    active_offer_count = IntegerField(null=True, blank=True, default=0)

    objects = NeighborhoodManager()

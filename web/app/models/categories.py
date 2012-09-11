from django.db.models import Manager
from django.utils.http import urlquote

from knotis import KnotisModel
from contents import Content, ContentTypes
from foreignkeynonrel.models import ForeignKeyNonRel


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
            name=content_name
        )


class Category(KnotisModel):
    content_root = ForeignKeyNonRel(Content, related_name='category_root')
    name = ForeignKeyNonRel(Content, related_name='category_name')

    objects = CategoryManager()

    def short_name(self):
        return self.name.value.strip().lower()[:3]

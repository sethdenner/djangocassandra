from django.db.models import Manager
from django.utils.http import urlquote

from knotis import KnotisModel
from contents import Content
from foreignkeynonrel.models import ForeignKeyNonRel

class CategoryManager(Manager):
    def create_category(
        self,
        user,
        name
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))

        content_root = Content(
            content_type='5.0',
            user=user,
            name=backend_name
        )
        content_root.save()

        content_name = Content(
            content_type='5.1',
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )
        content_name.save()

        category = Category(name=content_name)
        category.save()


class Category(KnotisModel):
    name = ForeignKeyNonRel(Content, related_name='category_name')

    objects = CategoryManager()

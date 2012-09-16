from django.db.models import IntegerField, CharField, Manager
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
            name=content_name,
            name_short=backend_name[:3]
        )


class Category(KnotisModel):
    content_root = ForeignKeyNonRel(Content, related_name='category_root')
    name = ForeignKeyNonRel(Content, related_name='category_name')
    name_short = CharField(max_length=3, null=True, blank=True, default=None)
    active_offer_count = IntegerField(null=True, blank=True, default=0)

    objects = CategoryManager()

    def short_name(self):
        return self.name_short

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

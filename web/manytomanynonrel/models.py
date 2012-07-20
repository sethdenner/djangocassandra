from djangotoolbox.fields import ListField
from views import ManyToManyFormField


class ManyToManyModelField(ListField):
    def formfield(self, **kwargs):
        return ManyToManyFormField(**kwargs)

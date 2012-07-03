from django.db import models

class MatrixField(models.Field):
    """A field type for storing matrixes."""

    def get_data(self, obj):
        return getattr(obj, self.field_name)

    def set_data(self, obj, data):
        setattr(obj, self.field_name, 'pickle the matrix')

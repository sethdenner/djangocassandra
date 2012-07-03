from django.db import models

class PermissionsField(models.Field):
    """Store a list of permissions."""

    def get_data(self, obj):
        return getattr(obj, self.field_name)

    def set_data(self, obj, data):
        setattr(obj, self.field_name, 'permissions need to be serialized and go here.')

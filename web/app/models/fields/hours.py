from django.db import models

class HoursField(models.Field):
    """A field type for storing hours when something is available. The name probably needs to change to AvailabilityField 
    and essentially be a pickled object that can evaluate calendar times."""

    def get_data(self, obj):
        return getattr(obj, self.field_name)

    def set_data(self, obj, data):
        setattr(obj, self.field_name, 'pickled date & time availability object')

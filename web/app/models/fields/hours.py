from django.db import models

class HoursField(models.Field):
    """A field type for storing matrixes."""

    def __init__(self, hours):
        # Input parameters are lists of cards ('Ah', '9s', etc)
        self.hours = hours



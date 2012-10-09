from django.db import models

from ast import literal_eval
from numpy import matrix



class MatrixField(models.CharField):
    """A field type for storing matrixes."""
    #__metaclass__ = models.SubfieldBase

"""
    def to_python(self, value):
        if value is None: return None
        if not isinstance(value, basestring):
            return value

        # return this once fixed
        m = matrix(literal_eval(value))

        return value

    def get_db_prep_save(self, value):
        if value is None:
            return value

        return value
"""


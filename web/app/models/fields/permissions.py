from django.db import models
from django.contrib.auth.models import Permission
import pickle

class PermissionsField(models.Field):
    """Store a list of permissions."""
    description = "A hand of cards (bridge style)"

    __metaclass__ = models.SubfieldBase

    #def __init__(self, *args, **kwargs):
    #    pass

    def db_type(self, connection):
        return 'text'

    def to_python(self, value):
        #if isinstance(value, unicode):
        #    return value
        #if isinstance(value, Permission):
        #    return value

        if len(value) == 0:
            return None
        #raise Exception(value)

        #permission = value
        #permission = pickle.loads(value)
        #if (type(permission) !=  Permission):
        #    raise ValidationError("Invalid input for a Permission instance")
        return value

    def get_prep_value(self, value):
        return value
        #return pickle.dumps(value)

    def get_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        #elif lookup_type == 'in':
        #    return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)


    #def formfield(self, **kwargs):
    #    # This is a fairly standard way to set up some defaults
    #    # while letting the caller override them.
    #    defaults = {'form_class': MyFormField}
    #    defaults.update(kwargs)
    #    return super(PermissionField, self).formfield(**defaults)

    def get_internal_type(self):
        return 'PermissionField'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

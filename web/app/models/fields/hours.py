from app.models.fields.binary import PickledObjectField

class HoursField(PickledObjectField):
    """A field type for storing hours when something is available. The name probably needs to change to AvailabilityField 
    and essentially be a pickled object that can evaluate calendar times."""

    """
    def to_python(self, value):
        if value is None: return None
        if not isinstance(value, basestring): return value
        return pickle.loads(base64.b64decode(value))
 
    def get_db_prep_save(self, value):
        if value is None: return
        return base64.b64encode(pickle.dumps(value))
        """

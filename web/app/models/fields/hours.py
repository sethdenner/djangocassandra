from app.models.fields.binary import PickledObjectField
from datetime import datetime
from abc import ABCMeta

class TimeSpan:
    __metaclass__ = ABCMeta
    
    def __init__(self):
        pass

    def __iter__(self):
        pass

    def next(self):
        pass

class TimeSpanSimple(TimeSpan):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __iter__(self):
        return(self)
        pass

    def next(self):
        return(self)
        pass

class TimeSpanPeriodic(TimeSpanSimple):
    def __init__(self, start, end, delta):
        self.delta = delta
        super(TimeSpanPeriodic, self).__init__(start,end)

class TimeSpanAnual(TimeSpanSimple):
    def __init__(self, start, end, holiday):
        """ Holiday needs to be an enum of sorts """
        self.holiday = holiday
        super(TimeSpanSimple, self).__init__(start,end)

class TimeSpanCompound(TimeSpan):
    def __init__(self, timespans):
        """ Holiday needs to be an enum of sorts """
        assert(isinstance(list, timespans))
        self.timespans = timespans

    def __iter__(self):
        return self.timespans.__iter__

    """
    I don't know that this is the correct way to implement this.
    def next(self):
        return self.timespans.__iter__
    """

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

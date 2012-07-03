from django.db.models import CharField, ForeignKey, DateTimeField, FloatField

from app.models.knotis import KnotisModel

from contents import Content

"""

Everything that users do is considered an action.

Analytics are not the same between "Things I do" and "Things that are done to my stuff."

The analytics for a user's actions which we plan to reward are different from things like accesses by people against resources.

"""

class ActionType(KnotisModel):
    ACTION_TYPES = (
        ('0', 'view content'),
        ('1', 'upload content')
    )

    value = CharField(max_length=30, choices=ACTION_TYPES)
    created_by = CharField(max_length=1024)
    pub_date = DateTimeField('date published')
    
    def __unicode__(self):
        output_array = [
            self.value,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])


# this isn't ready at all..
class Action(KnotisModel):
     content = ForeignKey('self')
     pub_date = DateTimeField('date published')



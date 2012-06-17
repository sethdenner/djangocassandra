from django.db.models import AutoField, CharField
from app.models.knotis import KnotisModel

class EndpointType(KnotisModel):
    id = AutoField(primary_key=True)
    
    ENDPOINT_TYPES = (
        ('0', 'email'),
        ('1', 'phone')
    )
    value = CharField(max_length=30, choices=ENDPOINT_TYPES)
    
    def __unicode__(self):
        output_array = [
            self.value,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])

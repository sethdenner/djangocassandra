from django.db import models
from web.app.knotis.db import KnotisModel

class EndpointType(KnotisModel):
    id = models.AutoField(primary_key=True)
    
    ENDPOINT_TYPES = (
        ('0', 'email'),
        ('1', 'phone')
    )
    value = models.CharField(max_length=30, choices=ENDPOINT_TYPES)
    
    def __unicode__(self):
        output_array = [
            self.value,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])

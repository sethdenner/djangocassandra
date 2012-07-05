from django.db import models
from web.app.models.knotis import KnotisModel
from djangotoolbox.fields import EmbeddedModelField

class TestModel(KnotisModel):
    name  = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.name
    
class EmbeddedModelFieldTest(KnotisModel):
    embedded = EmbeddedModelField(TestModel)
    other = models.CharField(max_length=200)

#    -----
#create column family app_testmodel
#  with column_type = 'Standard'
#  and comparator = 'UTF8Type'
#  and default_validation_class = 'BytesType'
#  and key_validation_class = 'BytesType'
#  and read_repair_chance = 0.1
#  and dclocal_read_repair_chance = 0.0
#  and gc_grace = 864000
#  and min_compaction_threshold = 4
#  and max_compaction_threshold = 32
#  and replicate_on_write = true
#  and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
#  and caching = 'KEYS_ONLY'
#  and compression_options = {'sstable_compression' : 'org.apache.cassandra.io.compress.SnappyCompressor'};
#



USE knotis;
CREATE TABLE offer_offercollection (
  key blob,
  content_type_id blob,
  deleted blob,
  neighborhood blob,
  PRIMARY KEY (key)
) WITH COMPACT STORAGE AND
  bloom_filter_fp_chance=0.010000 AND
  caching='KEYS_ONLY' AND
  comment='' AND
  dclocal_read_repair_chance=0.000000 AND
  gc_grace_seconds=864000 AND
  index_interval=128 AND
  read_repair_chance=0.100000 AND
  replicate_on_write='true' AND
  populate_io_cache_on_flush='false' AND
  default_time_to_live=0 AND
  speculative_retry='NONE' AND
  memtable_flush_period_in_ms=0 AND
  compaction={'class': 'SizeTieredCompactionStrategy'} AND
  compression={'sstable_compression': 'LZ4Compressor'};

CREATE INDEX offer_offercollection_content_type_id_idx ON offer_offercollection (content_type_id);

CREATE INDEX offer_offercollection_deleted_idx ON offer_offercollection (deleted);

CREATE INDEX offer_offercollection_neighborhood_idx ON offer_offercollection (neighborhood);



CREATE TABLE offer_offercollectionitem (
  key blob,
  content_type_id blob,
  deleted blob,
  offer_collection_id blob,
  offer_id blob,
  PRIMARY KEY (key)
) WITH COMPACT STORAGE AND
  bloom_filter_fp_chance=0.010000 AND
  caching='KEYS_ONLY' AND
  comment='' AND
  dclocal_read_repair_chance=0.000000 AND
  gc_grace_seconds=864000 AND
  index_interval=128 AND
  read_repair_chance=0.100000 AND
  replicate_on_write='true' AND
  populate_io_cache_on_flush='false' AND
  default_time_to_live=0 AND
  speculative_retry='NONE' AND
  memtable_flush_period_in_ms=0 AND
  compaction={'class': 'SizeTieredCompactionStrategy'} AND
  compression={'sstable_compression': 'LZ4Compressor'};

CREATE INDEX offer_offercollectionitem_content_type_id_idx ON offer_offercollectionitem (content_type_id);

CREATE INDEX offer_offercollectionitem_deleted_idx ON offer_offercollectionitem (deleted);

CREATE INDEX offer_offercollectionitem_offer_collection_id_idx ON offer_offercollectionitem (offer_collection_id);

CREATE INDEX offer_offercollectionitem_offer_id_idx ON offer_offercollectionitem (offer_id);


use knotis;

CREATE TABLE stripe_stripecustomer (
  key blob,
  content_type_id blob,
  deleted blob,
  identity_id blob,
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

CREATE INDEX stripe_stripecustomer_content_type_id_idx ON stripe_stripecustomer (content_type_id);

CREATE INDEX stripe_stripecustomer_deleted_idx ON stripe_stripecustomer (deleted);

CREATE INDEX stripe_stripecustomer_identity_id_idx ON stripe_stripecustomer (identity_id);

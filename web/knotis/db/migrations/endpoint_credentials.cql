use knotis;

CREATE TABLE endpoint_credentials (
  key blob,
  content_type_id blob,
  deleted blob,
  endpoint_id blob,
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

CREATE INDEX endpoint_credentials_content_type_id_idx ON endpoint_credentials (content_type_id);

CREATE INDEX endpoint_credentials_deleted_idx ON endpoint_credentials (deleted);

CREATE INDEX endpoint_credentials_endpoint_id_idx ON endpoint_credentials (endpoint_id);

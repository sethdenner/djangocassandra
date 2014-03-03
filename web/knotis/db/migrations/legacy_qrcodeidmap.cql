USE knotis;
CREATE TABLE legacy_qrcodeidmap (
  key blob,
  new_qrcode_id blob,
  old_id blob,
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

CREATE INDEX legacy_qrcodeidmap_new_qrcode_id_idx ON legacy_qrcodeidmap (new_qrcode_id);

CREATE INDEX legacy_qrcodeidmap_old_id_idx ON legacy_qrcodeidmap (old_id);

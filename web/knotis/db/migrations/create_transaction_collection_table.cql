USE knotis;
CREATE TABLE transaction_transactioncollection (
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

CREATE INDEX transaction_transactioncollection_content_type_id_idx ON transaction_transactioncollection (content_type_id);

CREATE INDEX transaction_transactioncollection_deleted_idx ON transaction_transactioncollection (deleted);

CREATE INDEX transaction_transactioncollection_neighborhood_idx ON transaction_transactioncollection (neighborhood);



CREATE TABLE transaction_transactioncollectionitem (
  key blob,
  content_type_id blob,
  deleted blob,
  page blob,
  transaction_collection_id blob,
  transaction_id blob,
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

CREATE INDEX transaction_transactioncollectionitem_content_type_id_idx ON transaction_transactioncollectionitem (content_type_id);

CREATE INDEX transaction_transactioncollectionitem_deleted_idx ON transaction_transactioncollectionitem (deleted);

CREATE INDEX transaction_transactioncollectionitem_page_idx ON transaction_transactioncollectionitem (page);

CREATE INDEX transaction_transactioncollectionitem_transaction_collection_id_idx ON transaction_transactioncollectionitem (transaction_collection_id);

CREATE INDEX transaction_transactioncollectionitem_transaction_id_idx ON transaction_transactioncollectionitem (transaction_id);


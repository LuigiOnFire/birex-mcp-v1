-- init_schema_anomaly.sql
-- psql -U postgres -d anomaly_data -f init_schema_anomaly.sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
DROP TABLE IF EXISTS anomaly_data;
CREATE TABLE anomaly_data (
    time TIMESTAMPTZ NOT NULL,
    process_id INTEGER,
    anomaly_detected BOOLEAN NOT NULL
) WITH (
  tsdb.hypertable,
  tsdb.partition_column='time'
);
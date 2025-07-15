-- init_schema.sql
-- psql -U postgres -d uptime_db -f init_schema.sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
DROP TABLE IF EXISTS process_uptime;
CREATE TABLE process_uptime (
    time TIMESTAMPTZ NOT NULL,
    process_id INTEGER,
    status     BOOLEAN NOT NULL
) WITH (
  tsdb.hypertable,
  tsdb.partition_column='time'
);
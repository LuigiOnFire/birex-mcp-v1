import logging
import asyncio
import asyncpg
import random
from datetime import datetime, timezone

PROCESS_RATES = {
    1111: 0.00,  # no failures
    1112: 0.01,  # 1% failure rate
    1113: 0.05,  # 5% failure rate
    1114: 0.10   # 10% failure rate
}

INTERVAL_SECONDS = 5  # adjust as needed

async def init_table():
    conn = await asyncpg.connect("postgresql://postgres@db:5432/anomaly_data")

    try:
        await conn.execute("""
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
        """)
    finally:
        await conn.close()

    print("Table initialized.")


async def insert_data():
    conn = await asyncpg.connect("postgresql://postgres@db:5432/anomaly_data")

    try:
        while True:
            now = datetime.now(timezone.utc)

            # Simulate data insertion
            values = []
            for pid, fail_rate in PROCESS_RATES.items():
                anomaly = random.random() < fail_rate
                values.append((now, pid, anomaly))

            await conn.executemany("""
                INSERT INTO anomaly_data (time, process_id, anomaly_detected)
                VALUES ($1, $2, $3)
            """, values)

            print(f"[{now.isoformat()}] Inserted {len(values)} rows.")
            await asyncio.sleep(INTERVAL_SECONDS)

    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(init_table())
    asyncio.run(insert_data())
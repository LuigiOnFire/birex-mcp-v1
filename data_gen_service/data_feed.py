import logging
import asyncpg

async def insert_data():
    conn = await asyncpg.connect("postgresql://postgres@db:5432/anomaly_data")

    try
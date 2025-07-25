from typing import Any, Dict
import httpx
import os
import asyncpg
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP, Context
import logging

logging.basicConfig(level=logging.CRITICAL) # Set to DEBUG for more verbose output or CRITICAL for less
logger = logging.getLogger(__name__)


# Initialize FastMCP server
@asynccontextmanager
async def lifespan(server):
    conn = await asyncpg.connect("postgresql://postgres@db:5432/anomaly_data")
    try:
        yield type("C", (), {"db": conn})
    finally:
        await conn.close()

# mcp.lifespan = lifespan
mcp = FastMCP("SQL Query Agent", lifespan=lifespan)


@mcp.tool()
async def run_sql_query(ctx: Context, query: str) -> str:
    """ 
    Executes a read-only SQL query on the TimescaleDB database and returns the results as rows.
    Returns the results as a formatted string.
    """
    # WARNING: This current implementation is a bit risky.
    # Before doing anything in production, one should implement:
    # - query validation
    # - table whitelisting
    # - row limits
    # - query cost guards

    db = ctx.request_context.lifespan_context.db

    if not query.strip().lower().startswith("select"):
        return "Only SELECT queries are allowed."

    try:
        rows = await db.fetch(query)
    except Exception as e:
        return f"SQL Error: {str(e)}"

    if not rows:
        return "Query executed successfully, but returned no results."

    # Format the results as a simple table
    headers = list(rows[0].keys())
    lines = [", ".join(headers)]

    out_values = []
    for row in rows:
        row_values = []
        for h in headers:
            val = row[h]
            row_values.append(str(val))
            out_values.append(row_values)
    
    for row in out_values:
        formatted = ", ".join(row)
        lines.append(formatted)

    table_str = "\n".join(lines)
    logging.debug("Formatted output table:\n%s", table_str)
    
    return table_str

@mcp.tool()
async def describe_tables(ctx: Context) -> str:
    """
    Returns the schema of relevant tables, including column names and types.
    Helps the LLM formulate correct queries.
    """
    db = ctx.request_context.lifespan_context.db
    result = await db.fetch("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    schema = ""
    for row in result:
        schema += f"{row['table_name']}.{row['column_name']} ({row['data_type']})\n"
    return schema

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="http", host="0.0.0.0", port=3300)

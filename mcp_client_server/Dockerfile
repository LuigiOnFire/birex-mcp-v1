FROM python:3.11-slim

COPY mcp_client /mcp_client
COPY mcp_server /mcp_server
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "mcp_client/client.py", "mcp_server/server.py"]

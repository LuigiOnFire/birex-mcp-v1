FROM python:3.11-slim

COPY data_feed.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "data_feed.py"]

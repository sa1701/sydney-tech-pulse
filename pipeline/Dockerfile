FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY schema.sql .
COPY src/ src/

ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "-m", "pulse.run"]

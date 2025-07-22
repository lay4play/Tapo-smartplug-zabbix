FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        zabbix-sender \
        gcc \
        libffi-dev \
	build-essential \
        libssl-dev && \
    pip install --no-cache-dir python-kasa && \
    # Clean up build deps & APT cache to slim the final image
    apt-get purge -y --auto-remove gcc libffi-dev libssl-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY src/main.py ./

ENTRYPOINT ["python", "/app/main.py"]

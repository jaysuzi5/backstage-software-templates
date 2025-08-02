FROM python:3.12.0-alpine

COPY requirements.txt /tmp

# Install build dependencies separately
RUN apk add --no-cache --virtual .build-deps \
        gcc musl-dev libffi-dev python3-dev cargo

# Upgrade pip and install Python packages
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

# Clean up build dependencies
RUN apk del .build-deps

COPY ./src /src

CMD ["opentelemetry-instrument", "--logs_exporter", "otlp", "--traces_exporter", "otlp", "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "src.app:app"]

FROM python:3.12.0-alpine

COPY requirements.txt /tmp

# Add necessary build tools
RUN apk add --no-cache --virtual .build-deps \
        gcc musl-dev libffi-dev python3-dev cargo \
    && pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && apk del .build-deps  # optionally clean up

COPY ./src /src

CMD ["opentelemetry-instrument", "--logs_exporter", "otlp", "--traces_exporter", "otlp", "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "src.app:app"]

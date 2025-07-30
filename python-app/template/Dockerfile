FROM python:3.12.0-alpine

COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

COPY ./src /src

CMD ["opentelemetry-instrument", "--logs_exporter", "otlp", "--traces_exporter", "otlp", "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "src.app:app"]
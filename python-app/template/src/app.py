from flask import Flask, jsonify, request, g
import datetime
import time
import logging
import socket
import uuid
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry import metrics

# Setup Metrics
exporter = OTLPMetricExporter(endpoint="http://otel-collector.monitoring.svc.cluster.local:4317", insecure=True)
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("${{values.app_name}}")
request_counter = meter.create_counter(
    name="http_server_requests_total",
    unit="1",
    description="Total number of HTTP requests received"
)

# Setup Logging
logger = logging.getLogger()
logger.handlers.clear()
logger.propagate = False
logger.setLevel(logging.INFO)
logger.addHandler(LoggingHandler())

# Setup Flask app
app = Flask(__name__)

# Instrument Flask app with OTEL Trace and Metrics
FlaskInstrumentor().instrument_app(app)

# Middleware
@app.before_request
def start_request():
    g.transaction_id = str(uuid.uuid4())  # Store in Flask's context (thread-safe)
    g.start_time = time.time()
    logger.info({
        "event": "Request",
        "transaction_id": g.transaction_id,
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "hostname": socket.gethostname()
    })

@app.after_request
def finish_response(response):
    duration = time.time() - getattr(g, 'start_time', time.time())
    request_counter.add(
        1,
        {
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "hostname": socket.gethostname()
        }
    )
    logger.info({
        "event": "Response",
        "transaction_id": getattr(g, 'transaction_id', None),
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration_seconds": round(duration, 4),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "hostname": socket.gethostname()
    })
    return response


# Define endpoints
@app.route('/api/${{values.app_name}}/v1/info')
def info():
    return jsonify({
        'hostname': socket.gethostname(),
        'env': '${{values.app_env}}',
        'app_name': '${{values.app_name}}',
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
    })


@app.route('/api/${{values.app_name}}/v1/health')
def health():
    return jsonify({'status': 'UP'}), 200


# Main app entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


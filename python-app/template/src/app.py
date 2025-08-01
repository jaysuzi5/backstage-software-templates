from flask import Flask, jsonify, request, g
import datetime
import logging
import socket
import uuid
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from prometheus_flask_exporter import PrometheusMetrics


# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if not any(isinstance(h, LoggingHandler) for h in logger.handlers):
    logger.addHandler(LoggingHandler())

# Setup Flask app
app = Flask(__name__)

# Instrument Flask app with OTEL Trace and Metrics
FlaskInstrumentor().instrument_app(app)
metrics = PrometheusMetrics(app)

# Setup for Pre- and Post-Request Logging
import time

# Middleware
@app.before_request
def start_request():
    g.transaction_id = str(uuid.uuid4())  # Store in Flask's context (thread-safe)
    g.start_time = time.time()
    logger.info({
        "event": "request_started",
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
    logger.info({
        "event": "request_finished",
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
        'app_name': '${{values.app_name}}'
    })


@app.route('/api/${{values.app_name}}/v1/health')
def health():
    return jsonify({'status': 'UP'}), 200


# Main app entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


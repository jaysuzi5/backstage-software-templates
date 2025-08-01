from flask import Flask, jsonify
import datetime
import logging
import socket
import json
import uuid
from opentelemetry._logs import get_logger_provider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (PeriodicExportingMetricReader,)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Setup Flask app
app = Flask(__name__)

# Setup OTEL MeterProvider and exporter
exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# Create meter and counter
meter = metrics.get_meter(__name__)
endpoint_counter = meter.create_counter(
    name="endpoint_requests_total",
    description="Counts how many times /hello endpoint is called",
)






logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add OTEL handler if not already present
if not any(isinstance(h, LoggingHandler) for h in logger.handlers):
    logger.addHandler(LoggingHandler())

class StructuredMessage:
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return json.dumps({
            "message": self.message,
            **self.kwargs,
            "service": "${{values.app_name}}",
            "hostname": socket.gethostname(),
            "timestamp": datetime.datetime.now().isoformat()
        })


tracer = trace.get_tracer("${{values.app_name}}.tracer")
# meter = metrics.get_meter("${{values.app_name}}.meter")

# endpoint_counter = meter.create_counter(
#     name="endpoint_requests_total",
#     description="Counts how many times endpoints are called",
# )




app = Flask(__name__)

@app.route('/api/${{values.app_name}}/v1/info')
def info():
    with tracer.start_as_current_span("info") as info_span:
        transaction_id = str(uuid.uuid4())
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
        info_span.set_attribute("transaction_id", transaction_id)
        endpoint_counter.add(1, {"endpoint": "info"})

        logger.info(StructuredMessage(
            'info called from ${{values.app_name}}',
            transactionId=transaction_id,            
            time=current_time,
            endpoint='info',
            hostname=socket.gethostname(),
            environment='${{values.app_env}}'
        ))
        return jsonify({
            'time': current_time,
            'hostname': socket.gethostname(),
            'env': '${{values.app_env}}',
            'app_name': '${{values.app_name}}'
        })


@app.route('/api/${{values.app_name}}/v1/health')
def health():
    with tracer.start_as_current_span("health") as health_span:
        transaction_id = str(uuid.uuid4())
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
        health_span.set_attribute("transaction_id", transaction_id)
        endpoint_counter.add(1, {"endpoint": "health"})
        logger.info(StructuredMessage(
            'info called from ${{values.app_name}}',
            transactionId=transaction_id,
            time=current_time,
            endpoint='health',
            status='UP',
            environment='${{values.app_env}}'
        ))    
        return jsonify({'status': 'UP'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


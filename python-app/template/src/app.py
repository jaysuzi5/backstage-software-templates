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
meter = metrics.get_meter("${{values.app_name}}.meter")

call_counter = meter.create_counter(
    "${{values.app_name}}_calls_total",
    description="The number of endpoint calls",
    unit="1"
)



app = Flask(__name__)

@app.route('/api/${{values.app_name}}/v1/info')
def info():
    with tracer.start_as_current_span("info") as info_span:
        transaction_id = str(uuid.uuid4())
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
        info_span.set_attribute("transaction_id", transaction_id)
        call_counter.add(1, {"endpoint": "info"})

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
        call_counter.add(1, {"endpoint": "health"})
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


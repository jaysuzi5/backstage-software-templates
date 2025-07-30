from flask import Flask, jsonify
import datetime
import logging
import socket
import json
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

app = Flask(__name__)

# Set up OTEL logging with JSON formatting
resource = Resource.create({
    "service.name": "otel-test6",
    "service.version": "1.0",
    "environment": "dev"
})

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# JSON formatter that works with OTEL
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "stack_trace": self.formatException(record.exc_info) if record.exc_info else None
        }
        return json.dumps(log_record)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)


@app.route('/api/${{values.app_name}}/v1/info')
def info():
    logger.info('info called')
    return jsonify({
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d"),
        'hostname': socket.gethostname(),
        'message': 'Changed to info endpoint',
        'status': 'UP',
        'env': '${{values.app_env}}',
        'app_name': '${{values.app_name}}'
    })


@app.route('/api/${{values.app_name}}/v1/health')
def health():
    logger.info('health called')
    return jsonify({'status': 'UP'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


from flask import Flask, jsonify
import datetime
import logging
import socket
import json
from opentelemetry._logs import get_logger_provider
from opentelemetry.sdk._logs import LoggingHandler

# Basic logging configuration that preserves OTEL integration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add OTEL handler if not already present
if not any(isinstance(h, LoggingHandler) for h in logger.handlers):
    logger.addHandler(LoggingHandler())

# Keep your JSON formatter for console only
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "service": "${{values.app_name}}",
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None)
        })

# Configure console handler separately
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)


app = Flask(__name__)

@app.route('/api/${{values.app_name}}/v1/info')
def info():
    app.logger.info('info called from ${{values.app_name}}')
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
    app.logger.info('health called from ${{values.app_name}}')
    return jsonify({'status': 'UP'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


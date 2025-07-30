from flask import Flask, jsonify
import datetime
import logging
import socket
import json
from opentelemetry._logs import get_logger_provider

app = Flask(__name__)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "stack_trace": self.formatException(record.exc_info) if record.exc_info else None,
            # Include OTEL context if available
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None)
        })

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Remove existing handlers (avoid duplicate logs)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add JSON formatter to console
json_handler = logging.StreamHandler()
json_handler.setFormatter(JsonFormatter())
logger.addHandler(json_handler)



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


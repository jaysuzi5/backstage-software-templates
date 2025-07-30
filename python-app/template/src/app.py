from flask import Flask, jsonify
import datetime
import logging
import socket
import json
from opentelemetry._logs import get_logger_provider

# Define formatters first
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "stack_trace": self.formatException(record.exc_info) if record.exc_info else None,
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None)
        })

class SplunkHecFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": int(record.created * 1000),  # Epoch milliseconds
            "host": socket.gethostname(),
            "source": "flask-app",
            "sourcetype": "_json",
            "event": {
                "message": record.getMessage(),
                "level": record.levelname,
                "logger": record.name,
                "stack_trace": self.formatException(record.exc_info) if record.exc_info else None,
                "trace_id": getattr(record, "trace_id", None),
                "span_id": getattr(record, "span_id", None)
            }
        })

# Configure logging before creating the Flask app
def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)

# Configure logging first
configure_logging()


# Now start the app
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


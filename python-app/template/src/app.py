import datetime
import logging
import os
import requests
import socket
import time
import traceback
import uuid
from flask import Flask, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.instrumentation.flask import FlaskInstrumentor


# Setup Logging
logger = logging.getLogger()
logger.handlers.clear()
logger.propagate = False
logger.setLevel(logging.INFO)
logger.addHandler(LoggingHandler())

# Setup Flask app
app = Flask(__name__)

# Setup Database
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
db = SQLAlchemy(app)

# Instrument Flask app with OTEL Trace and Metrics
FlaskInstrumentor().instrument_app(app)


# Middleware
@app.before_request
def start_request():
    g.transaction_id = str(uuid.uuid4())  # Store in Flask's context (thread-safe)
    g.start_time = time.time()
    g.method = request.method
    g.path = request.path
    g.endpoint = request.path.rsplit('/', 1)[-1] 


    logger.info({
        "level": "INFO",
        "event": "Request",
        "method": request.method,
        "path": request.path,
        "endpoint": g.endpoint,
        "remote_addr": request.remote_addr,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "transaction_id": g.transaction_id
    })

@app.after_request
def finish_response(response):
    duration = time.time() - getattr(g, 'start_time', time.time())
    logger.info({
        "level": "INFO",
        "event": "Response",
        "method": getattr(g, 'method', None),
        "path": getattr(g, 'path', None),
        "endpoint": getattr(g, 'endpoint', None),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "duration_seconds": round(duration, 4),
        "status": response.status_code,
        "transaction_id": getattr(g, 'transaction_id', None)
    })
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    stack_trace = traceback.format_exc()
    logger.error({
        "level": "ERROR",
        "event": "Unhandled Exception",
        "method": getattr(g, 'method', None),
        "path": getattr(g, 'path', None),
        "endpoint": getattr(g, 'endpoint', None),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'exception': str(e),
        "stack_trace": stack_trace,
        "transaction_id": getattr(g, 'transaction_id', None)
    })

    # Optional: Return JSON response to client
    return {
        "error": "Unhandled Exception",
        "transaction_id": getattr(g, 'transaction_id', None)
    }, 500


# Define model used with sample()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))


# Define endpoints
@app.route('/api/${{values.app_name}}/v1/sample')
def sample():
    # External API call (instrumented by opentelemetry-instrumentation-requests)
    response = requests.get('https://api.chucknorris.io/jokes/random')

    # Database query (instrumented by opentelemetry-instrumentation-sqlalchemy)
    users = db.session.execute(db.select(User)).scalars().all()
    
    return {"api_data": response.text, "users": [user.name for user in users]}


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


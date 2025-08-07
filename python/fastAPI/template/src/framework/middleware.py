import logging
import os
import socket
import time
import uuid
import datetime
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from opentelemetry.sdk._logs import LoggingHandler

# Configure logger
logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)

if os.getenv("PYTEST_CURRENT_TEST"):
    # Simple stdout handler for tests
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
else:
    try:
        from opentelemetry.sdk._logs import LoggingHandler
        logger.addHandler(LoggingHandler())
    except Exception:
        # If OTEL isn't available or misconfigured, revert to simple logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        transaction_id = str(uuid.uuid4())
        start_time = time.time()

        path = request.url.path
        method = request.method
        parts = path.strip('/').split('/')
        endpoint = parts[-1]
        app_name = parts[1] if len(parts) >= 4 and parts[0] == 'api' and parts[2] == 'v1' else None

        logger.info({
            "level": "INFO",
            "event": "Request",
            "method": method,
            "app_name": app_name,
            "endpoint": endpoint,
            "path": path,
            "remote_addr": request.client.host,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "hostname": socket.gethostname(),
            "transaction_id": transaction_id
        })

        try:
            response = await call_next(request)
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.error({
                "level": "ERROR",
                "event": "Unhandled Exception",
                "method": method,
                "app_name": app_name,
                "endpoint": endpoint,
                "path": path,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "exception": str(e),
                "stack_trace": stack_trace,
                "transaction_id": transaction_id
            })
            raise e

        duration = time.time() - start_time
        logger.info({
            "level": "INFO",
            "event": "Response",
            "method": method,
            "app_name": app_name,
            "endpoint": endpoint,
            "path": path,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration_seconds": round(duration, 4),
            "status": response.status_code,
            "transaction_id": transaction_id
        })

        return response

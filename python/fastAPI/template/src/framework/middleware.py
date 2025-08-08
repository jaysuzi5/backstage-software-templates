import logging
import socket
import time
import uuid
import datetime
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from opentelemetry.sdk._logs import LoggingHandler

# Configure logger
middleware_logger = logging.getLogger("middleware")
middleware_logger.setLevel(logging.INFO)

# Only add a handler if none exists (prevents duplication in test runners)
if not middleware_logger.handlers:
    middleware_logger.addHandler(LoggingHandler())


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        transaction_id = str(uuid.uuid4())
        start_time = time.time()

        path = request.url.path
        method = request.method
        parts = path.strip('/').split('/')
        endpoint = parts[-1]
        app_name = parts[1] if len(parts) >= 4 and parts[0] == 'api' and parts[2] == 'v1' else None

        middleware_logger.info({
            "level": "INFO",
            "event": "Request",
            "method": method,
            "service": app_name,
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
            middleware_logger.error({
                "level": "ERROR",
                "event": "Unhandled Exception",
                "method": method,
                "service": app_name,
                "endpoint": endpoint,
                "path": path,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "exception": str(e),
                "stack_trace": stack_trace,
                "transaction_id": transaction_id
            })
            raise e

        duration = time.time() - start_time
        middleware_logger.info({
            "level": "INFO",
            "event": "Response",
            "method": method,
            "path": path,
            "endpoint": endpoint,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration_seconds": round(duration, 4),
            "status": response.status_code,
            "transaction_id": transaction_id
        })

        return response
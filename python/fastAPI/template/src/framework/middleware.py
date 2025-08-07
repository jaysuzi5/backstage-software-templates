import logging
import os
import socket
import time
import uuid
import datetime
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

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
        # IMPORTANT: Move these imports inside the else block
        from opentelemetry.sdk._logs import LoggingHandler
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk._logs import LoggerProvider
        
        # Create a proper logger provider with resource
        logger_provider = LoggerProvider(
            resource=Resource.create({"service.name": "your-service-name"})
        )
        logger.addHandler(LoggingHandler(logger_provider=logger_provider))
    except Exception as e:
        print(f"Failed to initialize OpenTelemetry: {e}")
        # Fallback to simple logging if OTEL fails
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

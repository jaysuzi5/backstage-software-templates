import logging
import socket
import time
import uuid
import datetime
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from opentelemetry.sdk._logs import LoggingHandler
from starlette.responses import StreamingResponse
import json

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
        app_name = parts[2] if len(parts) >= 4 and parts[0] == 'api' and parts[1] == 'v1' else None

        # Read request body
        request_body = None
        if method in ("POST", "PUT", "PATCH"):
            try:
                request_body = await request.body()
                if request_body:
                    try:
                        request_body = json.loads(request_body.decode('utf-8'))
                    except json.JSONDecodeError:
                        request_body = request_body.decode('utf-8')
            except Exception:
                request_body = None

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
            "transaction_id": transaction_id,
            "request_body": request_body,
            "query_params": dict(request.query_params)
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
                "transaction_id": transaction_id,
                "request_body": request_body
            })
            raise e

        # Process response body
        response_body = b''
        if isinstance(response, StreamingResponse):
            async for chunk in response.body_iterator:
                response_body += chunk

            # Rebuild the streaming response
            async def new_body_iterator():
                yield response_body

            response = StreamingResponse(
                content=new_body_iterator(),
                status_code=response.status_code,
                media_type=response.media_type,
                headers=response.headers
            )
        else:
            response_body = response.body

        # Parse response body if possible
        parsed_response_body = None
        if response_body:
            try:
                parsed_response_body = json.loads(response_body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                try:
                    parsed_response_body = response_body.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    parsed_response_body = str(response_body)

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
            "transaction_id": transaction_id,
            "response_body": parsed_response_body
        })

        return response
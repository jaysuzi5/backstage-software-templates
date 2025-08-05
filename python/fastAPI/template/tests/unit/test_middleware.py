import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from starlette.responses import Response
from middleware import LoggingMiddleware  # adjust import path as needed


@pytest.mark.asyncio
async def test_logging_middleware_normal_flow():
    # Arrange
    request = MagicMock()
    request.url.path = "/api/myapp/v1/sample"
    request.method = "GET"
    request.client.host = "1.2.3.4"

    response = Response(status_code=200)
    call_next = AsyncMock(return_value=response)

    middleware = LoggingMiddleware(lambda req: None)

    # Patch logger.info to monitor calls
    with patch("middleware.logger.info") as mock_info, patch("middleware.logger.error") as mock_error:
        # Act
        result = await middleware.dispatch(request, call_next)

        # Assert
        assert result.status_code == 200
        assert call_next.await_count == 1
        assert mock_info.call_count >= 2  # At least request and response log

        # Check that no error logs were called
        mock_error.assert_not_called()

        # Inspect one of the info call arguments to verify keys
        logged_args = mock_info.call_args[0][0]  # First call, first positional arg
        assert "event" in logged_args
        assert logged_args["event"] in {"Request", "Response"}
        assert logged_args["method"] == "GET"
        assert logged_args["path"] == "/api/myapp/v1/sample"
        assert "transaction_id" in logged_args


@pytest.mark.asyncio
async def test_logging_middleware_exception_flow():
    # Arrange
    request = MagicMock()
    request.url.path = "/api/myapp/v1/sample"
    request.method = "POST"
    request.client.host = "5.6.7.8"

    async def raise_exc(req):
        raise ValueError("Test exception")

    call_next = AsyncMock(side_effect=raise_exc)
    middleware = LoggingMiddleware(lambda req: None)

    with patch("middleware.logger.info") as mock_info, patch("middleware.logger.error") as mock_error:
        # Act / Assert
        with pytest.raises(ValueError, match="Test exception"):
            await middleware.dispatch(request, call_next)

        # There should be at least one info log for request
        mock_info.assert_called()
        # There should be one error log for exception
        mock_error.assert_called_once()

        error_log_arg = mock_error.call_args[0][0]
        assert error_log_arg["event"] == "Unhandled Exception"
        assert "stack_trace" in error_log_arg
        assert error_log_arg["exception"] == "Test exception"
        assert error_log_arg["method"] == "POST"
        assert "transaction_id" in error_log_arg


@pytest.mark.asyncio
async def test_logging_middleware_app_name_and_endpoint_parsing():
    # Arrange various paths
    cases = [
        ("/api/myapp/v1/sample", "sample", "myapp"),
        ("/api/myapp/v1", "v1", "myapp"),
        ("/api/otherapp/v1/test/extra", "extra", "otherapp"),
        ("/notapi/test/path", "path", None),
        ("/api/myapp/v2/sample", "sample", None),
        ("/api/myapp/v1", "v1", "myapp"),
    ]

    middleware = LoggingMiddleware(lambda req: None)

    for path, expected_endpoint, expected_app in cases:
        request = MagicMock()
        request.url.path = path
        request.method = "GET"
        request.client.host = "1.2.3.4"

        call_next = AsyncMock(return_value=Response(status_code=200))

        with patch("middleware.logger.info") as mock_info:
            await middleware.dispatch(request, call_next)

            # The first info call contains "Request" event and app_name logic
            call_args = mock_info.call_args[0][0]
            parts = path.strip('/').split('/')
            assert call_args["endpoint"] == expected_endpoint

            if len(parts) >= 4 and parts[0] == 'api' and parts[2] == 'v1':
                assert call_args.get("app_name") == expected_app
            else:
                assert call_args.get("app_name") is None

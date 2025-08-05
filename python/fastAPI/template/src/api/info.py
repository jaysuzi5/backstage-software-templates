import socket
import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/${{values.app_name}}/v1/info")
def info():
    """
    Application information endpoint.

    Returns:
        dict: A dictionary containing runtime information about the application.
              Includes:
                - hostname (str): The system hostname where the app is running.
                - env (str): The deployment environment (e.g., dev, test, prod).
                - app_name (str): The name of the application.
                - time (str): The current server time, formatted as "HH:MM:SS AM/PM on YYYY-MM-DD".
    """
    return {
        'hostname': socket.gethostname(),
        'env': '${{values.app_env}}',
        'app_name': '${{values.app_name}}',
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
    }

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
                - app_name (str): The name of the application.
                - description (str): A brief description of the application.
                - env (str): The environment/namespace of the application.
                - time (str): The current server time, formatted as "HH:MM:SS AM/PM on YYYY-MM-DD".
    """
    return {
        'hostname': socket.gethostname(),
        'app_name': '${{values.app_name}}',
        'description': '${{values.description}}',
        'app_env': '${{values.app_env}}',
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
    }

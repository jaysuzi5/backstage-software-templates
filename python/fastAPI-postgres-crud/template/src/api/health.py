from fastapi import APIRouter

router = APIRouter()

@router.get("/api/${{values.app_name}}/v1/health")
def health():
    """
    Health check endpoint.

    Returns:
        dict: A simple dictionary indicating the health status of the service.
              The key 'status' will be set to 'UP' to signal that the service is
              running and responsive.
    """
    return {"status": "UP"}

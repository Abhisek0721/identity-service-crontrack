# users/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = None
        if isinstance(response.data, dict):
            message = next(iter(response.data.values()))[0] if response.data else "Validation error"
        else:
            message = "Validation error"

        custom_response_data = {
            "data": None,
            "message": message,
            "error": response.data
        }
        return Response(custom_response_data, status=response.status_code)

    return Response({
        "data": None,
        "message": "An unknown error occurred.",
        "error": [str(exc)]
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

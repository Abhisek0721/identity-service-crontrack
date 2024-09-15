# users/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = None
        # Extract a more meaningful message if available
        if isinstance(response.data, dict):
            # Handle specific cases for token validation
            if "detail" in response.data:
                message = response.data["detail"]
            elif "messages" in response.data:
                message = response.data["messages"][0]["message"] if response.data["messages"] else "Internal Server Error"
            else:
                # Handle generic case
                first_error = next(iter(response.data.values()), None)
                if isinstance(first_error, list):
                    message = first_error[0] if first_error else message
                else:
                    message = str(first_error)
        elif isinstance(response.data, list):
            # Handle list-based errors
            message = response.data[0] if response.data else "Internal Server Error"

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

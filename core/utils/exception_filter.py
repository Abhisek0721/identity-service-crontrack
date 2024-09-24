# users/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = None
        errors = response.data

        # Extract a more meaningful message if available
        if isinstance(errors, dict):
            # Handle specific cases for token validation and other exceptions
            message = errors.get("detail", "An error occurred.")
            if "messages" in errors:
                # Assuming messages is a list of error objects
                message = errors["messages"][0]["message"] if errors["messages"] else "Internal Server Error"
            else:
                # Get the first error message from the dictionary
                first_error = next(iter(errors.values()), None)
                if isinstance(first_error, list):
                    message = first_error[0] if first_error else "Internal Server Error"
                elif isinstance(first_error, str):
                    message = first_error
                else:
                    message = str(first_error)
        elif isinstance(errors, list):
            message = errors[0] if errors else "Internal Server Error"

        # Build a consistent response structure
        custom_response_data = {
            "data": None,
            "message": str(message),  # Ensure the message is always a string
            "errors": errors
        }
        return Response(custom_response_data, status=response.status_code)

    # Fallback for unknown errors
    return Response({
        "data": None,
        "message": "An unknown error occurred.",
        "errors": [str(exc)]
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

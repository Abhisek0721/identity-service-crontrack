# users/utils.py
from rest_framework import status
from django.http import JsonResponse

def api_response(data=None, message="", error=None, status=status.HTTP_200_OK):
    if error is None:
        error = []
    response_data = {
        "data": data,
        "message": message,
        "error": error,
    }
    return JsonResponse(data=response_data, status=status)

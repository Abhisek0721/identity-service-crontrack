from rest_framework_simplejwt.tokens import AccessToken

def decode_jwt_token(request):
    try:
        jwt_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
        if not jwt_token:
            return None  # Handle missing token case
        decoded_token = AccessToken(jwt_token)
        user_id = decoded_token['user_id']
        full_name = decoded_token['full_name']
        email = decoded_token['email']
        # Additional claims handling
        return {
            "user_id": user_id, 
            "full_name": full_name, 
            "email": email
        }
    except Exception as e:
        # Handle decoding errors
        print(f"Error decoding token: {str(e)}")
        return None
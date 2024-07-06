from rest_framework_simplejwt.tokens import AccessToken

def decode_jwt_token(jwt_token):
    try:
        decoded_token = AccessToken(jwt_token)
        user_id = decoded_token['user_id']
        full_name = decoded_token['full_name']
        email = decoded_token['email']
        # Additional claims handling
        return user_id, full_name, email
    except Exception as e:
        # Handle decoding errors
        print(f"Error decoding token: {str(e)}")
        return None, None, None
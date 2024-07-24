import uuid
import json
from django.core.cache import cache

def generate_and_save_token(email, verification_type, role=None, workspace_id=None):
    token = str(uuid.uuid4())
    data = {
        'email': email,
        'type': verification_type,
        'role': role,
        'workspace_id': workspace_id
    }
    cache.set(token, json.dumps(data), timeout=86400)  # Token valid for 1 day
    return token

def get_data_from_token(token):
    data = cache.get(token)
    if data:
        data = json.loads(data)
        cache.delete(token)
        return data
    return None
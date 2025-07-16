import jwt
from datetime import datetime, timedelta
from django.conf import settings
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def generate_jwt(user):
    payload = {
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

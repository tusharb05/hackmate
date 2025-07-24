import jwt
import os
from rest_framework.exceptions import AuthenticationFailed

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def verify_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise AuthenticationFailed("user_id not found")

    return user_id
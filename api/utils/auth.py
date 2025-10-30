from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from api.config.config import Config

BACKEND_API_SECRET_KEY = Config.BACKEND_API_SECRET_KEY

security = HTTPBearer()


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    JWT token validation function.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, BACKEND_API_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token",
                            headers={"WWW-Authenticate": "Bearer"}, )


def get_current_user(payload: dict = Depends(verify_jwt_token)) -> dict:
    """
    User information extraction function.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found in token")

    user_data =  {
        "user_id": user_id,
        "username": payload.get("username"),
        "role": payload.get("role")
    }
    return user_data

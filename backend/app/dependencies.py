from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token

security = HTTPBearer(auto_error=False)

def get_current_user_payload(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    """
    FastAPI dependency to verify JWT token and return full decoded payload.
    Raises 401 if missing or invalid.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_current_user(payload: dict = Depends(get_current_user_payload)) -> str:
    """
    FastAPI dependency to authenticate requests using Bearer JWT.
    Returns the authenticated user_id.
    """
    return payload["sub"]

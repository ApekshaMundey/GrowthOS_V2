import jwt
from fastapi import HTTPException, status
from app.config import settings

_jwks_client = None

def get_jwks_client() -> jwt.PyJWKClient | None:
    """Returns a singleton PyJWKClient instance targeting SUPABASE_JWKS_URL."""
    global _jwks_client
    jwks_url = settings.SUPABASE_JWKS_URL
    if not jwks_url:
        return None
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(jwks_url)
    return _jwks_client

def verify_token(token: str) -> dict:
    """
    Verifies a Supabase-issued JWT using SUPABASE_JWKS_URL.
    Returns the decoded JWT payload on success.
    Raises HTTPException(401) on missing/invalid/expired tokens.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwks_url = settings.SUPABASE_JWKS_URL
    if not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication configuration missing (SUPABASE_JWKS_URL)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256", "HS256"],
            options={"verify_aud": False}
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier (sub)",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

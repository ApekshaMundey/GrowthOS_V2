from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/test")
def auth_test(user_id: str = Depends(get_current_user)):
    """Protected verification endpoint for authentication."""
    return {"user_id": user_id}

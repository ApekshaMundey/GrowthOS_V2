from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_current_user_payload
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(payload: dict = Depends(get_current_user_payload)):
    """Fetch current user's profile data."""
    user_id = payload["sub"]
    email = payload.get("email", "")
    return UserService.get_or_create_profile(user_id=user_id, email=email)

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    update_data: UserUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update current user's profile data."""
    return UserService.update_profile(user_id=user_id, update_data=update_data)

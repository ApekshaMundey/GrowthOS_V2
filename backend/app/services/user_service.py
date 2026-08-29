from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate

class UserService:
    @staticmethod
    def get_or_create_profile(user_id: str, email: str = "") -> UserResponse:
        """Retrieve user profile by ID, auto-creating a default profile if not yet created."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            user = UserRepository.create_user_profile(user_id=user_id, email=email or f"{user_id}@example.com")
        return UserResponse.model_validate(user)

    @staticmethod
    def update_profile(user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update fields on user's profile."""
        # Convert Pydantic model to dict, filtering out unset fields
        fields_to_update = update_data.model_dump(exclude_unset=True, by_alias=False)
        if not fields_to_update:
            existing = UserRepository.get_by_id(user_id)
            if not existing:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
            return UserResponse.model_validate(existing)

        updated_user = UserRepository.update_user(user_id, fields_to_update)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
        return UserResponse.model_validate(updated_user)

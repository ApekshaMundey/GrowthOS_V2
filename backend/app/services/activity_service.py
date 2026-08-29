import math
from typing import Optional
from fastapi import HTTPException, status
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
)

class ActivityService:
    @staticmethod
    def create_activity(user_id: str, payload: ActivityCreate) -> ActivityResponse:
        """Create a new activity owned by user_id."""
        data_dict = {
            "activity_type": payload.activity_type.value,
            "title": payload.title,
            "content": payload.content,
            "source": payload.source.value,
            "source_metadata": payload.source_metadata,
            "activity_date": payload.activity_date.isoformat() if payload.activity_date else None,
        }
        record = ActivityRepository.create(user_id, data_dict)
        return ActivityResponse.model_validate(record)

    @staticmethod
    def get_activity(activity_id: str, user_id: str) -> ActivityResponse:
        """Get activity by ID ensuring user ownership."""
        record = ActivityRepository.get_by_id(activity_id, user_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id '{activity_id}' not found."
            )
        return ActivityResponse.model_validate(record)

    @staticmethod
    def list_activities(
        user_id: str,
        page: int = 1,
        limit: int = 20,
        source: Optional[str] = None,
        activity_type: Optional[str] = None
    ) -> ActivityListResponse:
        """List activities for user_id with pagination and filters."""
        if page < 1:
            page = 1
        if limit < 1:
            limit = 20
        elif limit > 100:
            limit = 100

        items_data, total = ActivityRepository.list_activities(
            user_id=user_id,
            page=page,
            limit=limit,
            source=source,
            activity_type=activity_type,
        )

        items = [ActivityResponse.model_validate(item) for item in items_data]
        total_pages = math.ceil(total / limit) if total > 0 else 0

        return ActivityListResponse(
            items=items,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )

    @staticmethod
    def update_activity(
        activity_id: str,
        user_id: str,
        payload: ActivityUpdate
    ) -> ActivityResponse:
        """Update activity fields for a user."""
        # First ensure activity exists and is owned by user
        existing = ActivityRepository.get_by_id(activity_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id '{activity_id}' not found."
            )

        updates = {}
        if payload.title is not None:
            updates["title"] = payload.title
        if payload.content is not None:
            updates["raw_content"] = payload.content
        if payload.activity_type is not None:
            updates["activity_type"] = payload.activity_type.value
        if payload.source_metadata is not None:
            updates["source_metadata"] = payload.source_metadata
        if payload.activity_date is not None:
            updates["activity_date"] = payload.activity_date.isoformat()

        if not updates:
            return ActivityResponse.model_validate(existing)

        updated_record = ActivityRepository.update(activity_id, user_id, updates)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id '{activity_id}' not found."
            )
        return ActivityResponse.model_validate(updated_record)

    @staticmethod
    def delete_activity(activity_id: str, user_id: str) -> None:
        """Delete activity by ID for user_id."""
        existing = ActivityRepository.get_by_id(activity_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id '{activity_id}' not found."
            )
        deleted = ActivityRepository.delete(activity_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id '{activity_id}' not found."
            )

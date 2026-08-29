from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from app.dependencies import get_current_user
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityTypeEnum,
    SourceEnum,
)
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new activity."""
    return ActivityService.create_activity(user_id=user_id, payload=payload)

@router.get("", response_model=ActivityListResponse)
def list_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[SourceEnum] = Query(None),
    activityType: Optional[ActivityTypeEnum] = Query(None),
    user_id: str = Depends(get_current_user)
):
    """List activities for the authenticated user."""
    source_val = source.value if source else None
    type_val = activityType.value if activityType else None
    return ActivityService.list_activities(
        user_id=user_id,
        page=page,
        limit=limit,
        source=source_val,
        activity_type=type_val,
    )

@router.get("/{id}", response_model=ActivityResponse)
def get_activity(
    id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a specific activity by ID."""
    return ActivityService.get_activity(activity_id=id, user_id=user_id)

@router.put("/{id}", response_model=ActivityResponse)
def update_activity(
    id: str,
    payload: ActivityUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update an activity by ID."""
    return ActivityService.update_activity(activity_id=id, user_id=user_id, payload=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete an activity by ID."""
    ActivityService.delete_activity(activity_id=id, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

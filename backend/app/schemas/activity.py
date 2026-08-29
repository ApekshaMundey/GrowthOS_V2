from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class ActivityTypeEnum(str, Enum):
    manual_note = "manual_note"
    project_update = "project_update"
    github_commit = "github_commit"
    youtube_video = "youtube_video"
    meeting_notes = "meeting_notes"
    research_note = "research_note"

class SourceEnum(str, Enum):
    Manual = "Manual"
    GitHub = "GitHub"

class StatusEnum(str, Enum):
    Pending = "Pending"
    Processing = "Processing"
    Completed = "Completed"
    Failed = "Failed"

class ActivityCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    activity_type: ActivityTypeEnum = Field(..., validation_alias="activityType", serialization_alias="activityType")
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source: SourceEnum = SourceEnum.Manual
    source_metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="sourceMetadata", serialization_alias="sourceMetadata")
    activity_date: Optional[datetime] = Field(None, validation_alias="activityDate", serialization_alias="activityDate")

class ActivityUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    activity_type: Optional[ActivityTypeEnum] = Field(None, validation_alias="activityType", serialization_alias="activityType")
    source_metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="sourceMetadata", serialization_alias="sourceMetadata")
    activity_date: Optional[datetime] = Field(None, validation_alias="activityDate", serialization_alias="activityDate")

class ActivityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    user_id: str = Field(..., serialization_alias="userId")
    activity_type: str = Field(..., serialization_alias="activityType")
    source: str
    title: str
    raw_content: str = Field(..., serialization_alias="rawContent")
    source_metadata: Optional[Dict[str, Any]] = Field(None, serialization_alias="sourceMetadata")
    activity_date: datetime = Field(..., serialization_alias="activityDate")
    status: str
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")

class ActivityListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: List[ActivityResponse]
    page: int
    limit: int
    total: int
    total_pages: int = Field(..., serialization_alias="totalPages")

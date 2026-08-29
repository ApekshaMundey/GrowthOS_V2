from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    name: str
    email: str
    profile_image: Optional[str] = Field(None, serialization_alias="profileImage")
    profession: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")

class UserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    name: Optional[str] = None
    profile_image: Optional[str] = Field(None, validation_alias="profileImage", serialization_alias="profileImage")
    profession: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None

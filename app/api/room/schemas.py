from pydantic import BaseModel, Field
from uuid import UUID


class CreateRoom(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Room name must be between 3 and 200 characters"
    )

    host_id: UUID
    
from datetime import datetime


class RoomResponse(BaseModel):
    id: UUID
    name: str
    host_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True 
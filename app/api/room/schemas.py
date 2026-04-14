from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.api.users.scemas import UserResponse


class CreateRoom(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Room name must be between 3 and 200 characters"
    )

    host_id: UUID


class RoomResponse(BaseModel):
    id: UUID
    name: str
    host_id: UUID
    is_active: bool
    code: str
    created_at: datetime

    class Config:
        from_attributes = True 
        
        
        
class ParticipantResponse(BaseModel):
    id : UUID
    room_id : UUID
    user_id : UUID
    joined_at : datetime
    is_connected : bool
    user : UserResponse
    
class RoomDetailResponse(BaseModel):
    user_id : UUID
    room: RoomResponse
    participants: list[ParticipantResponse]

    class Config:
            from_attributes = True
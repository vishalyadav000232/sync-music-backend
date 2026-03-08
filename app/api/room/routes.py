from fastapi import APIRouter, Depends
from app.services.interfaces.room_service_interface import RoomServiceInterface
from app.services.dependencies import get_room_service
from app.api.room.schemas import CreateRoom , RoomResponse
from uuid import UUID
from app.db.models.users import User
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/create", response_model=RoomResponse)
async def create_room(
    data: CreateRoom,
    service: RoomServiceInterface = Depends(get_room_service),
):
    
    return await service.create_room(data.dict())



@router.post("/join-by-code")
async def join_room(
    room_code: str,
  service: RoomServiceInterface = Depends(get_room_service),
    current_user: User = Depends(get_current_user)
):


    return await service.join_room(room_code , current_user.id)

@router.post("/{room_id}/leave")
async def leave_room(
    room_id: UUID,
  service: RoomServiceInterface = Depends(get_room_service),
    current_user: User = Depends(get_current_user)
):


    return await service.leave_room(room_id , current_user.id)

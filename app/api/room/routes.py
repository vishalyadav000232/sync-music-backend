from fastapi import APIRouter, Depends
from app.services.interfaces.room_service_interface import RoomServiceInterface
from app.services.dependencies import get_room_service
from app.api.room.schemas import CreateRoom , RoomResponse



router = APIRouter(prefix="/rooms" , tags=["Rooms"])

@router.post("/rooms", response_model=RoomResponse)
async def create_room(
    data: CreateRoom,
    service: RoomServiceInterface = Depends(get_room_service),
):
    return await service.create_room(data.dict())
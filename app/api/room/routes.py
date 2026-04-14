from fastapi import APIRouter, Depends, HTTPException, status
from app.services.interfaces.room_service_interface import RoomServiceInterface
from app.services.dependencies import get_room_service
from app.api.room.schemas import RoomResponse
from uuid import UUID
from app.db.models.users import User
from app.api.deps import get_current_user
from app.api.room.schemas import RoomDetailResponse


router = APIRouter()


@router.post("/create", response_model=RoomResponse)
async def create_room(
    name: str,
    service: RoomServiceInterface = Depends(get_room_service),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized user "
        )
    data = {
        "name": name,
        "host_id": current_user.id
    }

    return await service.create_room(data=data)


@router.post("/join-by-code", status_code=status.HTTP_200_OK, response_model=RoomDetailResponse)
async def join_room(
    room_code: str,
    service: RoomServiceInterface = Depends(get_room_service),
    current_user: User = Depends(get_current_user),
):
    return await service.join_room(room_code, current_user.id)


@router.post("/{room_id}/leave")
async def leave_room(
    room_id: UUID,
    service: RoomServiceInterface = Depends(get_room_service),
    current_user: User = Depends(get_current_user),
):


    return await service.leave_room(room_id , current_user.id)

from app.services.interfaces.room_service_interface import RoomServiceInterface
from app.db.dependencies.room import get_room_repository
from app.db.repositories.interface.room import RoomRepositoryInterface
from fastapi import Depends
from app.services.room_service import RoomService

def get_room_service(
    repo: RoomRepositoryInterface = Depends(get_room_repository),
) -> RoomServiceInterface:
    
    return RoomService(repo)
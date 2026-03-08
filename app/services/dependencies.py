from app.services.interfaces.room_service_interface import RoomServiceInterface
from app.db.dependencies.room import get_room_repository, get_room_participant
from app.db.repositories.interface.room import RoomRepositoryInterface
from fastapi import Depends
from app.services.room_service import RoomService
from app.db.repositories.interface.room_participants_interface import RoomParticipantRepositoryInterface
def get_room_service(
    repository: RoomRepositoryInterface = Depends(get_room_repository),
    repo :RoomParticipantRepositoryInterface = Depends(get_room_participant)
) -> RoomServiceInterface:
    
    return RoomService(repository , repo)
from uuid import UUID
from typing import List
from app.db.models.room import Room
from app.db.repositories.interface.room import RoomRepositoryInterface
from app.services.interfaces.room_service_interface import RoomServiceInterface
from fastapi import HTTPException , status

class RoomService(RoomServiceInterface):

    def __init__(self, repository: RoomRepositoryInterface):
        self.repository = repository

    async def create_room(self, data: dict) -> Room:
        
        if await self.repository.room_exists(data.get("name")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Room already exists"
            )

        return await self.repository.create_room(data)

    async def delete_room(self, room_id: UUID):
        return await self.repository.delete_room(room_id)

    async def get_active_rooms(self) -> List[Room]:
        pass
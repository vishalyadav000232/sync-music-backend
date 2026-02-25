from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from app.db.models.room import Room


class RoomServiceInterface(ABC):

    @abstractmethod
    async def create_room(self, data: dict) -> Room:
        pass

    @abstractmethod
    async def delete_room(self, room_id: UUID):
        pass

    @abstractmethod
    async def get_active_rooms(self) -> List[Room]:
        pass
    
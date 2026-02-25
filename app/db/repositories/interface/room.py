from abc import ABC , abstractmethod
from app.db.models.room import Room
from sqlalchemy.dialects.postgresql import UUID
from typing import List



class RoomRepositoryInterface(ABC):
    
    @abstractmethod
    async def create_room(self , data : dict)->Room:
        pass
    
    @abstractmethod
    async def delete_room(self, room_id :UUID):
        pass

    @abstractmethod
    async def get_active_rooms(self) -> List[Room]:
        pass
    
    @abstractmethod
    async def room_exists(self, name: str) -> bool:
       pass
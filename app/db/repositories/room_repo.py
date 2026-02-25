from app.db.repositories.interface.room import RoomRepositoryInterface
from app.db.repositories.base import BaseRepository
from app.db.models.room import Room

from sqlalchemy import select


class RoomRepository(BaseRepository[Room], RoomRepositoryInterface):

    async def create_room(self, data: dict):
        return await self.create(data)

    async def delete_room(self, room_id):
        return await self.delete(room_id)

    async def get_active_rooms(self):
        result = await self.db.execute(
            select(Room).where(Room.is_active == True)
        )
        return result.scalars().all()
    
    
    async def room_exists(self, name: str) -> bool:
        result = await self.db.execute(
            select(Room).where(Room.name == name)
        )
        room = result.scalar_one_or_none()
        return room is not None
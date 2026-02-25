from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.room import Room
from app.db.repositories.room_repo import RoomRepository
from app.db.repositories.interface.room import RoomRepositoryInterface


def get_room_repository(db: AsyncSession = Depends(get_db),) -> RoomRepositoryInterface:
    return RoomRepository(Room, db)
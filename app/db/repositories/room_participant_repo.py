        
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.models.participant import RoomParticipant
from app.db.repositories.interface.room_participants_interface import (
    RoomParticipantRepositoryInterface
)


class RoomParticipantRepository(RoomParticipantRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_room_and_user(
        self, room_id: UUID, user_id: UUID
    ) -> RoomParticipant | None:

        result = await self.db.execute(
            select(RoomParticipant).where(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self, room_id: UUID, user_id: UUID
    ) -> RoomParticipant:

        participant = RoomParticipant(
            room_id=room_id,
            user_id=user_id,
            is_connected=True
        )

        self.db.add(participant)
        return participant

    async def commit(self) -> None:
        await self.db.commit()
        

    async def get_participants_by_room(self, room_id):
        result = await self.db.execute(
        select(RoomParticipant)
        .options(joinedload(RoomParticipant.user))
        .where(RoomParticipant.room_id == room_id)
        )

        return result.scalars().all()
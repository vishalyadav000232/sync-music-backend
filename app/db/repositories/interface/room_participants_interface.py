from abc import ABC, abstractmethod
from uuid import UUID
from app.db.models.participant import RoomParticipant


class RoomParticipantRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_room_and_user(
        self, room_id: UUID, user_id: UUID
    ) -> RoomParticipant | None:
        pass

    @abstractmethod
    async def create(
        self, room_id: UUID, user_id: UUID
    ) -> RoomParticipant:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass
    @abstractmethod
    async def get_participants_by_room(self , room_id):
        pass
from uuid import UUID
from typing import List
from app.db.models.room import Room
from app.db.repositories.interface.room import RoomRepositoryInterface
from app.services.interfaces.room_service_interface import RoomServiceInterface
from fastapi import HTTPException , status
from app.db.repositories.interface.room_participants_interface import RoomParticipantRepositoryInterface
from app.api.room.schemas import CreateRoom
from app.utils.code_generate import room_code_genrate

class RoomService(RoomServiceInterface):

    def __init__(self, repository: RoomRepositoryInterface, repo :RoomParticipantRepositoryInterface ):
        self.repository = repository
        self.repo = repo

    async def create_room(self, data: CreateRoom) -> Room:
        
        if await self.repository.room_exists(data.get("name")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Room already exists"
            )
        
        room_data = {
            "name" : data["name"],
            "host_id": data["host_id"],
            "code" : room_code_genrate(),
        }

        return await self.repository.create_room(room_data)

    async def delete_room(self, room_id: UUID):
        return await self.repository.delete_room(room_id)

    async def get_active_rooms(self) -> List[Room]:
        
        active_rooms = await self.repository.get_active_rooms()
        result = []
        for room in active_rooms:
            participants = await self.repo.get_participants_by_room(room.id)
            if any(p.is_connected for p in participants):
                result.append(room)
        return result
    
    async def join_room(self, room_code: str, user_id: UUID):

   
        room = await self.repository.get_by_code(room_code=room_code)
        if not room:
            raise HTTPException(
            status_code=404,
            detail="Room not found"
        )
        participant = await self.repo.get_by_room_and_user(
            room.id, user_id
        )

        if participant:
            participant.is_connected = True
        else:
            participant = await self.repo.create(room.id, user_id)

        await self.repo.commit()

    
        return {
        "room_id": room.id,
        "room": room,
        "participant_id": participant.id
    }
        
    async def leave_room(self, room_id: UUID, user_id: UUID):
        participant = await self.repo.get_by_room_and_user(room_id, user_id)
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not in the room"
            )
        participant.is_connected = False
        await self.repo.commit()
        return {"message": "Left the room successfully"}
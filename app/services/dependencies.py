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

# from app.services.playback_service import PlaybackService
from app.db.repositories.playback_repo import PlaybackRepository
from app.db.dependencies.playback_deps import get_playback_repo

# def get_playback_service(
#     playback_repo :PlaybackRepository = Depends(get_playback_repo)
# ):
#     return PlaybackService(playback_repo
        
    # )
from fastapi import Depends
from app.services.playback__service import PlaybackService
# from app.services.playback__service import PlaybackSer÷vice

from app.redis.client import get_redis
from app.redis.playback_state import PlaybackState
from app.redis.distributed_lock import RedisLock
from app.redis.pubsub import PubSub


async def get_playback__service():

    redis_client = get_redis()

    state_repo = PlaybackState(redis_client)
    pub_sub = PubSub(redis_client)
    lock = RedisLock(redis_client)

    return PlaybackService(
        state_repo=state_repo,
        pub_sub=pub_sub,
        lock=lock
    )
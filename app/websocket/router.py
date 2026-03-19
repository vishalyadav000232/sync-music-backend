from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.websocket.manager import manager
from app.websocket.connection_registry import registry
from app.db.repositories.interface.room import RoomRepositoryInterface
from app.db.dependencies.room import get_room_repository
from app.db.dependencies.playback_deps import get_playback_repo
from app.db.repositories.playback_repo import PlaybackRepository
from app.services.dependencies import get_playback_service
from app.services.playback_service import PlaybackService
from app.core.security import TokenServiceInterface
from app.db.dependencies.token_deps import get_token_service

router = APIRouter()


@router.websocket("/ws/join/{room_code}/{user_id}")
async def join_room_ws(
    websocket: WebSocket,
    room_code: str,
    user_id: str,
    room_repo: RoomRepositoryInterface = Depends(get_room_repository),
    playback_repo: PlaybackRepository = Depends(get_playback_repo),
    playback_service: PlaybackService = Depends(get_playback_service),
    token_service: TokenServiceInterface = Depends(get_token_service)
):

    
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    token_user_id = await token_service.verify_access_token(token)

    if not token_user_id or token_user_id != user_id:
        await websocket.close(code=1008)
        return

   
    room = await room_repo.get_by_code(room_code)

    if not room:
        await websocket.close()
        return

    room_id = room.id
    host_id = room.host_id

  
    await manager.connect(room_id, websocket)

   
    await registry.ensure_listener(room_id, playback_repo, manager)

  
    state = await playback_repo.get_state(room_id)

    if state:
        await websocket.send_json({
            "type": "initial_state",
            "state": state
        })

    try:
        while True:

            message = await websocket.receive_json()
            action = message.get("type")

            print("Incoming:", message)

           
            if action == "PLAY":
                await playback_service.play(room_id, user_id, host_id)

       
            elif action == "PAUSE":
                await playback_service.pause(room_id, user_id, host_id)
           
            elif action == "SEEK":
                await playback_service.seek(
                    room_id,
                    message.get("position", 0),
                    user_id,
                    host_id
                )

         
            elif action == "chat_message":
                await playback_repo.publish_event(
                    room_id,
                    {
                        "event": {
                            "type": "chat_message",
                            "user": message.get("user"),
                            "text": message.get("text"),
                            "id":message.get("id")
                        }
                    }
                )

    except WebSocketDisconnect:

        # 🔌 DISCONNECT USER
        await manager.disconnect(room_id, websocket)

        # 🔥 IMPORTANT: RELEASE REGISTRY
        await registry.release(room_id)
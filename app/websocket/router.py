from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.websocket.manager import manager
from app.websocket.connection_registry import registry

from app.db.repositories.interface.room import RoomRepositoryInterface
from app.db.dependencies.room import get_room_repository

from app.services.dependencies import get_playback__service
from app.services.playback__service import PlaybackService

from app.core.security import TokenServiceInterface
from app.db.dependencies.token_deps import get_token_service

router = APIRouter()


@router.websocket("/ws/join/{room_code}/{user_id}")
async def join_room_ws(
    websocket: WebSocket,
    room_code: str,
    user_id: str,
    room_repo: RoomRepositoryInterface = Depends(get_room_repository),
    playback_service: PlaybackService = Depends(get_playback__service),
    token_service: TokenServiceInterface = Depends(get_token_service)
):

    #
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    token_user_id = await token_service.verify_access_token(token)

    if not token_user_id or token_user_id != user_id:
        await websocket.close(code=1008)
        return


    room = await room_repo.get_by_code(room_code)

    if not room:
        await websocket.close(code=1008, reason="Room not found")
        return

    room_id = room.id
    host_id = room.host_id

   
    await manager.connect(room_id, websocket)

    await registry.ensure_listener(room_id , playback_service.pub_sub , manager)

    state = await playback_service.state_repo.get(room_id)

    if state:
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "state": state,
            "source": "server"
        })

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("type")

            print("Incoming:", message)

            
            if action == "PLAY":
                await playback_service.play(
                    room_id,
                    user_id,
                    host_id,
                    message.get("song"),
                    message.get("index")
                )

            
            elif action == "PAUSE":
                await playback_service.pause(
                    room_id,
                    user_id,
                    host_id
                )

          
            elif action == "SEEK":
                await playback_service.seek(
                    room_id,
                    message.get("position", 0),
                    user_id,
                    host_id
                )

    
            elif action == "chat_message":
                await playback_service.pub_sub.publish(room_id, {
                    "event": {
                        "type": "chat_message",
                        "user": message.get("user"),
                        "text": message.get("text"),
                        "id": message.get("id"),
                        "source": "server"
                    }
                })

    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket)
        await registry.release(room_id)
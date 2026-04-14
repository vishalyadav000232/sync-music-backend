import asyncio
import logging
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.websocket.manager import manager
from app.websocket.connection_registry import registry

from app.db.repositories.interface.room import RoomRepositoryInterface
from app.db.dependencies.room import get_room_repository

from app.services.dependencies import get_playback__service  
from app.services.playback__service import PlaybackService

from app.core.security import TokenServiceInterface
from app.db.dependencies.token_deps import get_token_service

from app.sync_engine.heartbeat_scheduler import get_heartbeat
from app.sync_engine.time_calculator import TimeCalculator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/join/{room_code}/{user_id}")
async def join_room_ws(
    websocket: WebSocket,
    room_code: str,
    user_id: str,
    room_repo: RoomRepositoryInterface = Depends(get_room_repository),
    playback_service: PlaybackService = Depends(get_playback__service),
    token_service: TokenServiceInterface = Depends(get_token_service),
):
    await websocket.accept()
    heartbeat = get_heartbeat()
    listener_registered = False 


    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    token_user_id = await token_service.verify_access_token(token)
    if not token_user_id or str(token_user_id) != str(user_id):
        await websocket.close(code=1008, reason="Invalid token")
        return

    room = await room_repo.get_by_code(room_code)
    if not room:
        await websocket.close(code=1008, reason="Room not found")
        return

    room_id = str(room.id)
    host_id = str(room.host_id)

    # ── Connect ───────────────────────────────────────────────────────────────
    try:
        await manager.connect(room_id, websocket)

        if not heartbeat.is_running(room_id):
            await heartbeat.start(room_id)

        await registry.ensure_listener(room_id, playback_service.pub_sub, manager)
        listener_registered = True  

    except Exception:
        logger.exception("Connect error for user %s in room %s", user_id, room_id)
        await websocket.close()
        return

    # ── Initial SYNC ──────────────────────────────────────────────────────────
    try:
        state = await playback_service.state_repo.get(room_id)
        if state:
            current_position = TimeCalculator.current_position(state)

            await websocket.send_json({
                "type": "SYNC",
                "state": {**state, "position": current_position},
                "server_time": time.time(),
                "source": user_id,
            })
    except Exception:
        logger.exception("Initial sync error for user %s", user_id)

    # ── Message loop + Fix #3: cleanup finally mein ──────────────────────────
    try:
        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.receive_json(), timeout=30
                )
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "PING"})
                continue

            action = message.get("type")
            logger.debug("Action %s from user %s in room %s", action, user_id, room_id)

            if action in ("PLAY", "PAUSE", "SEEK") and user_id != host_id:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Only host can control playback",
                })
                continue

            try:
                if action == "PLAY":
                    await playback_service.play(
                        room_id, user_id, host_id,
                        message.get("song"),
                        message.get("index"),
                    )

                elif action == "PAUSE":
                    await playback_service.pause(room_id, user_id, host_id)

                elif action == "SEEK":
                    position = max(0.0, float(message.get("position", 0)))
                    await playback_service.seek(room_id, position, user_id, host_id)

                elif action == "chat_message":
                    await playback_service.pub_sub.publish(room_id, {
                        "event": {
                            "type": "chat_message",
                            "user": message.get("user"),
                            "text": message.get("text"),
                            "id": message.get("id"),
                            "source": user_id,
                        }
                    })

                else:
                    logger.debug("Unknown action: %s", action)

            except Exception:
                logger.exception("Action error for %s in room %s", action, room_id)

    except WebSocketDisconnect:
        logger.info("User %s disconnected from room %s", user_id, room_id)

    except Exception:
        logger.exception("Unexpected error in message loop for user %s", user_id)

    finally:
       
        await manager.disconnect(room_id, websocket)

        if manager.get_room_size(room_id) == 0:
            await heartbeat.stop(room_id)

        if listener_registered:  
            await registry.release(room_id)

        logger.info("Cleanup done for user %s in room %s", user_id, room_id)


@router.get("/debug/room/{room_id}")
def debug_room(room_id: str):
    hb = get_heartbeat()
    return {
        "users": manager.get_room_size(room_id),
        "heartbeat_running": hb.is_running(room_id),
    }
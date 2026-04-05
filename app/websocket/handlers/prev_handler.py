from app.redis.playback_state import PlaybackState
from app.utils.song import playlist
from app.websocket.manager import ConnectionManager



async def handle_prev(room_id , manager :ConnectionManager  , state : PlaybackState):
    
    
    if state.current_index == 0:
        state.current_index = len(playlist)-1
    else:
        state.current_index -= 1
    state.song = playlist[state.current_index -1]
    state.position = 0
    state.is_playing = True
    
    
    await manager.broadcast(
        room_id,
        {
            "type" : "PREV",
            "index": state.current_index,
            "song": state.song,
            "position": 0
        }
    )
    
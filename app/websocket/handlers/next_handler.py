
from app.utils.song import playlist
async def handle_next(room_id , manager , state):
    state.current_index = (state.current_index + 1) % len(playlist)
    state.song = playlist[state.current_index]
    state.position = 0
    state.is_playing = True
    
    await manager.broadcast(room_id, {
        "type": "NEXT",
        "index": state.current_index,
        "song": state.song,
        "position": 0
    })








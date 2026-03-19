class SyncService:

    def __init__(self, playback_repo, manager):
        self.repo = playback_repo
        self.manager = manager

    async def check_room_sync(self, room_id):

        state = await self.repo.get_state(room_id)

        if not state:
            return

        position = TimeCalculator.current_position(state)

        await self.manager.broadcast(room_id, {
            "type": "sync",
            "position": position
        })
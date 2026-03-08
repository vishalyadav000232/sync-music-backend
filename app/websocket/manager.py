from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        self.active_connections[room_id].append(websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket):

        connections = self.active_connections.get(room_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if len(connections) == 0:
            del self.active_connections[room_id]

    async def broadcast(self, room_id: str, message: str):

        connections = self.active_connections.get(room_id)

        if not connections:
            return

        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                await self.disconnect(room_id, connection)


manager = ConnectionManager()
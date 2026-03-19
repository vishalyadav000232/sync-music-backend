from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()  

        self.active_connections[room_id].add(websocket)

        print(f"User connected to room {room_id}")
        print(f"TOTAL CONNECTIONS: {len(self.active_connections[room_id])}")

    async def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)  # ✅ safe remove

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

        print(f"User disconnected from room {room_id}")
        print(f"TOTAL CONNECTIONS: {len(self.active_connections.get(room_id, []))}")

    async def broadcast(self, room_id: str, message: dict):
        connections = self.active_connections.get(room_id, set())

        print("Broadcast:", message)
        print("TOTAL CONNECTIONS:", len(connections))

        dead_connections = []

        for connection in connections:
            try:
                await connection.send_json(message)

            except Exception:
                
                dead_connections.append(connection)

        # cleanup dead sockets
        for conn in dead_connections:
            connections.discard(conn)

    def get_room_size(self, room_id: str) -> int:
        return len(self.active_connections.get(room_id, set()))


# Singleton
manager = ConnectionManager()
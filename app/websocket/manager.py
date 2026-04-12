from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import logging


logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        
        async with self._lock:
            if room_id not in self.active_connections:
                self.active_connections[room_id] = set()  

            self.active_connections[room_id].add(websocket)
        
        logger.info(f"User connected to room {room_id}")
        logger.info(f"TOTAL CONNECTIONS: {len(self.active_connections[room_id])}")

        print(f"User connected to room {room_id}")
        print(f"TOTAL CONNECTIONS: {len(self.active_connections[room_id])}")

    async def disconnect(self, room_id: str, websocket: WebSocket):
        
        async with self._lock:
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)

                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
                
        logger.info(f"User disconnected from room {room_id}")
        logger.info(
            f"TOTAL CONNECTIONS: {len(self.active_connections.get(room_id, []))}"
        )

        print(f"User disconnected from room {room_id}")
        print(f"TOTAL CONNECTIONS: {len(self.active_connections.get(room_id, []))}")
        
        
    async def _safe_broadcast(self, websocket: WebSocket, message):
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=2)
            return None
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}")
            return websocket


    async def broadcast(self, room_id: str, message: dict):
        
        async with self._lock:
            connections = self.active_connections.get(room_id, set()).copy()
        
        if not connections:
            logger.info(f"No active connections in room {room_id}")
            return

        logger.info(f"Broadcasting to {len(connections)} users in room {room_id}")

        tasks = [self._safe_broadcast(conn, message) for conn in connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        dead_connections = [conn for conn in results if conn]

        if dead_connections:
            async with self._lock:
                for conn in dead_connections:
                    if room_id in self.active_connections:
                        self.active_connections[room_id].discard(conn)

                
                if room_id in self.active_connections and not self.active_connections[room_id]:
                    del self.active_connections[room_id]
    def get_room_size(self, room_id: str) -> int:
            return len(self.active_connections.get(room_id, set()))


# Singleton
manager = ConnectionManager()
import asyncio
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        # await websocket.accept()
        async with self._lock:
            if room_id not in self.active_connections:
                self.active_connections[room_id] = set()
            self.active_connections[room_id].add(websocket)

        logger.info(
            "User connected to room %s — total: %d",
            room_id,
            len(self.active_connections[room_id]),
        )

    async def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]

        remaining = len(self.active_connections.get(room_id, set()))
        logger.info(
            "User disconnected from room %s — remaining: %d",
            room_id,
            remaining,
        )

    async def _safe_send(self, websocket: WebSocket, message: dict) -> WebSocket | None:
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=2)
            return None
        except Exception as e:
            logger.warning("WebSocket send failed: %s", e)
            return websocket

    async def broadcast(self, room_id: str, message: dict) -> None:
        async with self._lock:
            connections = self.active_connections.get(room_id, set()).copy()

        if not connections:
            return

        logger.debug("Broadcasting to %d users in room %s", len(connections), room_id)

        results = await asyncio.gather(
            *[self._safe_send(conn, message) for conn in connections],
            return_exceptions=True,
        )

        # Fix #13: sirf WebSocket objects discard karo, Exception nahi
        dead = [
            conn for conn in results
            if conn is not None and isinstance(conn, WebSocket)
        ]

        if dead:
            async with self._lock:
                for conn in dead:
                    if room_id in self.active_connections:
                        self.active_connections[room_id].discard(conn)
                if room_id in self.active_connections and not self.active_connections[room_id]:
                    del self.active_connections[room_id]

            logger.info("Removed %d dead connections from room %s", len(dead), room_id)

    def get_room_size(self, room_id: str) -> int:
        return len(self.active_connections.get(room_id, set()))


manager = ConnectionManager()
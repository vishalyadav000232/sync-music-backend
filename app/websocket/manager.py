from fastapi import WebSocket
from sqlalchemy.dialects.postgresql import UUID

class ConnectionManager():
    
    def __init__(self):
        self.activ_connection = {}
        
    async def connect(self , room_id : UUID , websocket: WebSocket):
        await websocket.accept()
        self.activ_connection.setdefault(room_id , []).append(websocket)
        
    async def broadcast(self ,room_id : UUID ,  messages : str):
        for connection in self.activ_connection.get(room_id , []):
            await connection.send_text(messages)






manager = ConnectionManager()
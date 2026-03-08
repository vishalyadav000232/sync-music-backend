from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.api.router import router as main_router
from app.redis.client import redis_client
from app.websocket.manager import manager
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "running"}


@app.get("/redis-test")
async def test():
    await redis_client.set("hello", "world")
    val = await redis_client.get("hello")
    return {"redis_value": val}

@app.websocket("/ws/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str):
    
    print("WS CONNECT:", room_id)
    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print("MESSAGE:", data)

            await manager.broadcast(room_id, data)

    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket)
        print("DISCONNECT:", room_id)
        
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.api.router import router as main_router
from app.redis.client import redis_client

app = FastAPI()

app.include_router(main_router)


@app.get("/")
async def root():
    return {"status": "running"}


@app.get("/redis-test")
async def test():
    await redis_client.set("hello", "world")
    val = await redis_client.get("hello")
    return {"redis_value": val}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You sent: {data}")

    except WebSocketDisconnect:
        print("Client disconnected")
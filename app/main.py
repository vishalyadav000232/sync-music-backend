from fastapi import FastAPI , WebSocket




app = FastAPI()


@app.get("/")
async def root():
    return {
        "status" : "running"
    }

from app.redis.client import redis_client

@app.get("/redis-test")
async def test():
    await redis_client.set("hello", "world")
    val = await redis_client.get("hello")
    return {"redis_value": val}


@app.websocket("/ws")
async def websoket_endpoint(websoket : WebSocket):
    await websoket.accept()
    
    while True:
        data = websoket.receive_text()
        await websoket.send_text({"data" : data})
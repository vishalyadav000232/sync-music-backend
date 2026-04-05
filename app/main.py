from fastapi import FastAPI
from app.api.router import router as main_router
from app.core.redis import redis_client
from fastapi.middleware.cors import CORSMiddleware
from app.websocket.router import router as websocket_router
app = FastAPI()


app.include_router(main_router)

app.include_router(websocket_router)

app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    return {"status": "running"}


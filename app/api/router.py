from fastapi import APIRouter
from app.api.room.routes import router as room_routes

router = APIRouter()

router.include_router(
    room_routes,
    prefix="/rooms",
    tags=["Rooms"]
)
from fastapi import APIRouter
from app.api.room.routes import router as room_routes
from app.api.users.auth import router as auth_router

# Main API router
router = APIRouter()

# Include Room routes
router.include_router(
    room_routes,
    prefix="/rooms",
    tags=["Rooms"]
)

# Include Auth routes
router.include_router(
    auth_router,
    prefix="/auth",   # make sure to add leading slash for consistency
    tags=["Auth"]
)
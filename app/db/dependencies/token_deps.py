from fastapi import Depends
from app.core.security import JWTTokenService
from app.db.dependencies.refresh_deps import get_refresh_service
from app.services.interfaces.refresh_token_interface import (
    RefreshTokenServiceInterface,
)


def get_token_service(
    refresh_service: RefreshTokenServiceInterface = Depends(get_refresh_service),
) -> JWTTokenService:
    
    return JWTTokenService(refresh_service=refresh_service)
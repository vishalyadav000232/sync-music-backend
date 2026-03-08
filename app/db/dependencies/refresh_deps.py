from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.repositories.refresh_token_repo import RefreshTokenRepository
from app.db.repositories.interface.refresh_token_interface import RefreshTokenInterFace
from app.services.refresh_token_service import RefreshTokenService


# dependecy for the repo



def get_refresh_repo(
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenRepository:
    
    return RefreshTokenRepository(db)

# Dependeny for refresh token service



def get_refresh_service(
    repo: RefreshTokenInterFace = Depends(get_refresh_repo),
) -> RefreshTokenService:
    
    return RefreshTokenService(repository=repo)
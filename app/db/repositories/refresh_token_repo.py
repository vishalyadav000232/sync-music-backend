from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models.refresh_token import RefreshToken
from app.db.repositories.base import BaseRepository
from app.db.repositories.interface.refresh_token_interface import (
    RefreshTokenInterFace,
)


class RefreshTokenRepository(
    BaseRepository[RefreshToken],
    RefreshTokenInterFace
):

    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

   
    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    
    async def is_valid(self, jti: str) -> bool:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.jti == jti,
                RefreshToken.revoke == False,
                RefreshToken.expire_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none() is not None


    async def revoke(self, jti: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.jti == jti)
            .values(revoke=True)
        )
        await self.db.commit()
from uuid import UUID
from datetime import datetime, timedelta

from app.db.models.refresh_token import RefreshToken
from app.db.repositories.refresh_token_repo import RefreshTokenRepository
from app.services.interfaces.refresh_token_interface import RefreshTokenServiceInterface



class RefreshTokenService(RefreshTokenServiceInterface):

    def __init__(self, repository: RefreshTokenRepository):
        self.repository = repository


    async def create_token(self, user_id: UUID, jti: str):
        expire_at = datetime.utcnow() + timedelta(days=7)

        token_data = {
            "user_id": user_id,
            "jti": jti,
            "expire_at": expire_at,
            "revoke": False,
        }

        return await self.repository.create(token_data)

    
    async def validate_token(self, jti: str) -> bool:
        return await self.repository.is_valid(jti)

    async def rotate_token(self, user_id: UUID, old_jti: str, new_jti: str):

       
        is_valid = await self.repository.is_valid(old_jti)
        if not is_valid:
            raise Exception("Invalid or revoked refresh token")

        
        await self.repository.revoke(old_jti)

        
        return await self.create_token(user_id, new_jti)

   
    async def revoke_token(self, jti: str):
        await self.repository.revoke(jti)
from abc import ABC, abstractmethod
from uuid import UUID


class RefreshTokenServiceInterface(ABC):

    @abstractmethod
    async def create_token(self, user_id: UUID, jti: str):
        pass

    @abstractmethod
    async def validate_token(self, jti: str) -> bool:
        pass

    @abstractmethod
    async def rotate_token(self, user_id: UUID, old_jti: str, new_jti: str):
        pass

    @abstractmethod
    async def revoke_token(self, jti: str):
        pass
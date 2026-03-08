from app.db.repositories.base import BaseRepository
from app.db.models.users import User
from sqlalchemy import select
from app.db.repositories.interface.user import UserRepositoryInterface



class UserRepository(BaseRepository[User], UserRepositoryInterface):

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str):
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
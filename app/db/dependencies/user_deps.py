
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends 
from app.db.session import get_db
from app.db.repositories.interface.user import UserRepositoryInterface
from app.db.repositories.user_repo import UserRepository
from app.db.models.users import User



def get_user_repository(db : AsyncSession = Depends(get_db))->UserRepositoryInterface:
    return UserRepository(User , db)
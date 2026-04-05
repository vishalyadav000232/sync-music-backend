from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.db.models.users import User
from app.db.repositories.interface.base import BaseRepositoryInterface
from typing import Sequence

class UserRepositoryInterface(BaseRepositoryInterface[User], ABC):
   

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        
        pass
    
    async def  totoal_active_user(self )-> Sequence[User]:
        pass
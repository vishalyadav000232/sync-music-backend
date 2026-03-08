from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.db.models.users import User
from app.db.repositories.interface.base import BaseRepositoryInterface


class UserRepositoryInterface(BaseRepositoryInterface[User], ABC):
    """
    Abstract repository interface for User entity.
    Inherits generic CRUD operations from BaseRepositoryInterface,
    and adds user-specific methods.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        Returns None if the user does not exist.
        """
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        Returns None if the user does not exist.
        """
        pass
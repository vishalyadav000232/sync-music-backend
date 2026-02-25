from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.dialects.postgresql import UUID


ModelType = TypeVar("ModelType")

class BaseRepositoryInterface(ABC, Generic[ModelType]):

    @abstractmethod
    async def create(self, obj_in: dict) -> ModelType:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def get_all(self) -> List[ModelType]:
        pass

    @abstractmethod
    async def delete(self, id: UUID):
        pass
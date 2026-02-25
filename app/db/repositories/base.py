from typing import Type, Generic, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.repositories.interface.base import BaseRepositoryInterface, ModelType
from sqlalchemy.dialects.postgresql import UUID


class BaseRepository(BaseRepositoryInterface[ModelType], Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        pk = getattr(self.model, "id")
        result = await self.db.execute(
            select(self.model).where(pk == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def delete(self, id: UUID) -> Optional[ModelType]:
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
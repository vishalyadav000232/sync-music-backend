from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, Index , func

class RoomParticipant(Base):
    
    __tablename__ = "room_participants"
    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="unique_room_user"),
        Index("idx_room_connected", "room_id", "is_connected"),
    )

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_connected: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

  
    room = relationship("Room", back_populates="participants")
    user = relationship("User", back_populates="room_participations")
from sqlalchemy import Column, String, Time, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Shift(Base):
    __tablename__ = "shifts"

    shift_id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(String(20), nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    description = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)

    created_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )

    updated_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships

    users = relationship(
        "User",
        back_populates="shift",
        foreign_keys="User.shift_id"
    )
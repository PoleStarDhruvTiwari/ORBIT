from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    labeller_id = Column(String(50), unique=True, nullable=True)

    role_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("roles.role_id"),
        nullable=False
    )

    shift_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("shifts.shift_id"),
        nullable=True
    )

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

    role = relationship(
        "Role",
        back_populates="users",
        foreign_keys=[role_id]
    )

    shift = relationship(
        "Shift",
        back_populates="users",
        foreign_keys=[shift_id]
    )

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
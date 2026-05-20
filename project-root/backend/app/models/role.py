from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(50),
        unique=True,
        nullable=False
    )


    description = Column(
        String,
        nullable=True
    )

    can_assign_tasks = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    can_create_tasks = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    can_review_quality = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    can_manage_users = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    can_view_reports = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    created_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )

    updated_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships

    users = relationship(
        "User",
        back_populates="role",
        foreign_keys="User.role_id"
    )
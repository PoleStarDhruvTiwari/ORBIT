# from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, func, UUID
# from sqlalchemy.dialects.postgresql import UUID as PGUUID
# from sqlalchemy.orm import relationship
# import uuid
# from app.database import Base

# class Role(Base):
#     __tablename__ = "roles"

#     role_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String(50), unique=True, nullable=False)  # 'super_admin','admin','qa','recorder'
#     description = Column(String, nullable=True)
#     can_assign_tasks = Column(Boolean, default=False)
#     can_create_tasks = Column(Boolean, default=False)
#     can_review_quality = Column(Boolean, default=False)
#     can_manage_users = Column(Boolean, default=False)
#     can_view_reports = Column(Boolean, default=False)
#     created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
#     updated_by = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)

#     users = relationship("User", back_populates="role")



# app/models/role.py

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

    description = Column(String, nullable=True)

    can_assign_tasks = Column(Boolean, default=False)
    can_create_tasks = Column(Boolean, default=False)
    can_review_quality = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_view_reports = Column(Boolean, default=False)

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
        back_populates="role",
        foreign_keys="User.role_id"
    )
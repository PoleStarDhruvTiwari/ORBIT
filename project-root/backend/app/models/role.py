from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


ROLE_NAME_ENUM = SAEnum(
    "super_admin",
    "admin",
    "qa",
    "recorder",
    name="role_name_enum",
    create_type=False,
)


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(ROLE_NAME_ENUM, unique=True, nullable=False)
    description = Column(Text, nullable=False)

    can_assign_tasks = Column(Boolean, nullable=False, server_default="false", default=False)
    can_create_tasks = Column(Boolean, nullable=False, server_default="false", default=False)
    can_review_quality = Column(Boolean, nullable=False, server_default="false", default=False)
    can_manage_users = Column(Boolean, nullable=False, server_default="false", default=False)
    can_view_reports = Column(Boolean, nullable=False, server_default="false", default=False)

    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    users = relationship(
        "User",
        back_populates="role",
        foreign_keys="User.role_id",
    )

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        foreign_keys="RolePermission.role_id",
    )

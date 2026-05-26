from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(BigInteger, primary_key=True, autoincrement=True)

    code = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="true", default=True)

    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        foreign_keys="RolePermission.permission_id",
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    role_permission_id = Column(BigInteger, primary_key=True, autoincrement=True)

    role_id = Column(BigInteger, ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(
        BigInteger, ForeignKey("permissions.permission_id", ondelete="CASCADE"), nullable=False
    )

    is_active = Column(Boolean, nullable=False, server_default="true", default=True)

    created_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    updated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    role = relationship("Role", back_populates="role_permissions", foreign_keys=[role_id])
    permission = relationship(
        "Permission", back_populates="role_permissions", foreign_keys=[permission_id]
    )

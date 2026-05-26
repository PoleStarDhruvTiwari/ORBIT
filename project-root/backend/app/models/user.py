from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("POSITION('@' IN email) > 1", name="chk_users_email"),
    )

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)

    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    labeller_id = Column(String(50), unique=True, nullable=False)

    role_id = Column(BigInteger, ForeignKey("roles.role_id"), nullable=False)
    shift_id = Column(BigInteger, ForeignKey("shifts.shift_id"), nullable=False)

    is_approved = Column(Boolean, nullable=False, server_default="false", default=False)
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

    role = relationship("Role", back_populates="users", foreign_keys=[role_id])
    shift = relationship("Shift", back_populates="users", foreign_keys=[shift_id])
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

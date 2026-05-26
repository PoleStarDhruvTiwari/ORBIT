from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


DEVICE_TYPE_ENUM = SAEnum(
    "mobile",
    "web",
    "tablet",
    "desktop",
    name="device_type_enum",
    create_type=False,
)


class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="chk_session_expiry"),
    )

    session_id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    device_id = Column(String(100), nullable=True)
    device_type = Column(DEVICE_TYPE_ENUM, nullable=False)

    hashed_refresh_token = Column(Text, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="sessions")

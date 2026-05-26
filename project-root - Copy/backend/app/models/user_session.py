from sqlalchemy import Column, String, Text, DateTime, ForeignKey, BigInteger, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(100), nullable=True)
    device_type = Column(String(20), nullable=True)  # mobile,web,tablet,desktop
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
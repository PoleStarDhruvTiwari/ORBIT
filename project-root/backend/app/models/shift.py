from sqlalchemy import (
    Column,
    BigInteger,
    Time,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


SHIFT_NAME_ENUM = SAEnum(
    "morning",
    "evening",
    "night",
    name="shift_name_enum",
    create_type=False,
)


class Shift(Base):
    __tablename__ = "shifts"
    __table_args__ = (
        CheckConstraint("start_time <> end_time", name="chk_shift_time"),
    )

    shift_id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(SHIFT_NAME_ENUM, unique=True, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    description = Column(Text, nullable=False)

    is_active = Column(Boolean, nullable=False, server_default="true", default=True)

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
        back_populates="shift",
        foreign_keys="User.shift_id",
    )

from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey, func

from app.database import Base


class TaskCategory(Base):
    __tablename__ = "task_categories"

    task_category_id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(String(100), unique=True, nullable=False)
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

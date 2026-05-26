from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


TASK_STATUS_ENUM = SAEnum(
    "draft", "approved", "rejected", "archived",
    name="task_status_enum", create_type=False,
)
TASK_TYPE_ENUM = SAEnum(
    "general", "niche",
    name="task_type_enum", create_type=False,
)
TASK_PRIORITY = SAEnum(
    "P0", "P1", "P2", "P3",
    name="task_priority", create_type=False,
)
TASK_ENVIRONMENT = SAEnum(
    "office/outdoor", "outdoor", "office",
    name="task_environment", create_type=False,
)


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "estimated_time_minutes BETWEEN 2 AND 15",
            name="chk_tasks_estimated_time",
        ),
    )

    task_id = Column(BigInteger, primary_key=True, autoincrement=True)

    task_key = Column(String(50), unique=True, nullable=False)

    category_id = Column(BigInteger, ForeignKey("task_categories.task_category_id"), nullable=False)
    environment = Column(TASK_ENVIRONMENT, nullable=False)
    priority = Column(TASK_PRIORITY, nullable=False, server_default="P2", default="P2")

    task_type = Column(TASK_TYPE_ENUM, nullable=False, server_default="general", default="general")

    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    task_script = Column(Text, nullable=True)

    estimated_time_minutes = Column(Integer, nullable=False)

    source_sheet_name = Column(String(255), nullable=True)
    source_row_id = Column(String(100), nullable=True)

    replicated_from = Column(BigInteger, ForeignKey("tasks.task_id"), nullable=True)

    status = Column(TASK_STATUS_ENUM, nullable=False, server_default="draft", default="draft")
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

    category = relationship("TaskCategory", foreign_keys=[category_id])
    parent = relationship("Task", remote_side=[task_id], foreign_keys=[replicated_from])

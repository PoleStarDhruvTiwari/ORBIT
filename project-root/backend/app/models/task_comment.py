from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


TASK_STATUS_ENUM = SAEnum(
    "draft", "approved", "rejected", "archived",
    name="task_status_enum", create_type=False,
)
TASK_COMMENT_KIND = SAEnum(
    "comment", "status_change", "skip_requested", "skip_approved",
    "skip_rejected", "submitted", "created", "assigned",
    name="task_comment_kind", create_type=False,
)


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    task_id = Column(BigInteger, ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False)
    author_id = Column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    kind = Column(TASK_COMMENT_KIND, nullable=False)
    body = Column(Text, nullable=True)

    status_from = Column(TASK_STATUS_ENUM, nullable=True)
    status_to = Column(TASK_STATUS_ENUM, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    task = relationship("Task", foreign_keys=[task_id])
    author = relationship("User", foreign_keys=[author_id])

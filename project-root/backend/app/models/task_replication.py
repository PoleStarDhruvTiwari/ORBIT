from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


TASK_ENVIRONMENT = SAEnum(
    "office/outdoor", "outdoor", "office",
    name="task_environment", create_type=False,
)


class TaskReplication(Base):
    __tablename__ = "task_replications"
    __table_args__ = (
        UniqueConstraint(
            "recording_log_id", "environment_identifier", name="uq_task_replication_environment"
        ),
    )

    task_replication_id = Column(BigInteger, primary_key=True, autoincrement=True)

    original_task_id = Column(BigInteger, ForeignKey("tasks.task_id"), nullable=False)
    recording_log_id = Column(
        BigInteger, ForeignKey("recording_logs.recording_log_id"), nullable=False
    )

    environment_type = Column(TASK_ENVIRONMENT, nullable=False)
    environment_identifier = Column(String(255), nullable=False)

    replicated_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)

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

    original_task = relationship("Task", foreign_keys=[original_task_id])
    recording_log = relationship("RecordingLog", foreign_keys=[recording_log_id])

from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


ASSIGNMENT_STATUS_ENUM = SAEnum(
    "assigned",
    "in_progress",
    "submitted",
    "qa_review_pending",
    "completed",
    "rejected",
    "skipped",
    "reassigned",
    name="assignment_status_enum",
    create_type=False,
)


class RecorderAssignment(Base):
    __tablename__ = "recorder_assignments"
    __table_args__ = (
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= created_at",
            name="chk_completed_at",
        ),
        UniqueConstraint("task_id", "recorder_id", "assigned_date", name="uq_assignment_per_day"),
    )

    recorder_assignment_id = Column(BigInteger, primary_key=True, autoincrement=True)

    task_id = Column(BigInteger, ForeignKey("tasks.task_id"), nullable=False)
    recorder_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    assigned_by = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    assigned_date = Column(Date, nullable=False, server_default=func.current_date())
    shift_id = Column(BigInteger, ForeignKey("shifts.shift_id"), nullable=False)

    status = Column(
        ASSIGNMENT_STATUS_ENUM, nullable=False, server_default="assigned", default="assigned"
    )

    completed_at = Column(DateTime(timezone=True), nullable=True)
    skipped_reason = Column(Text, nullable=True)
    reassigned_from_id = Column(
        BigInteger, ForeignKey("recorder_assignments.recorder_assignment_id"), nullable=True
    )

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

    task = relationship("Task", foreign_keys=[task_id])
    recorder = relationship("User", foreign_keys=[recorder_id])
    shift = relationship("Shift", foreign_keys=[shift_id])
    reassigned_from = relationship(
        "RecorderAssignment", remote_side=[recorder_assignment_id], foreign_keys=[reassigned_from_id]
    )

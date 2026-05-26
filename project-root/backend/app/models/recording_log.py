from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


RECORDING_STATUS_ENUM = SAEnum(
    "pending_review", "approved", "rejected", "rework_needed",
    name="recording_status_enum", create_type=False,
)


class RecordingLog(Base):
    __tablename__ = "recording_logs"
    __table_args__ = (
        CheckConstraint(
            "actual_time_minutes BETWEEN 0 AND 60",
            name="chk_recording_actual_time",
        ),
    )

    recording_log_id = Column(BigInteger, primary_key=True, autoincrement=True)

    assignment_id = Column(
        BigInteger,
        ForeignKey("recorder_assignments.recorder_assignment_id"),
        unique=True,
        nullable=False,
    )
    recorder_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)

    status = Column(
        RECORDING_STATUS_ENUM, nullable=False, server_default="pending_review", default="pending_review"
    )

    actual_time_minutes = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

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

    assignment = relationship("RecorderAssignment", foreign_keys=[assignment_id])
    recorder = relationship("User", foreign_keys=[recorder_id])

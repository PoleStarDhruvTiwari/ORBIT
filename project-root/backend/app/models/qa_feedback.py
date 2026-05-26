from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


FEEDBACK_CATEGORY_ENUM = SAEnum(
    "accuracy", "completeness", "speed", "guidelines",
    name="feedback_category_enum", create_type=False,
)


class QAFeedback(Base):
    __tablename__ = "qa_feedback"
    __table_args__ = (
        CheckConstraint("pass_rate BETWEEN 0 AND 100", name="chk_qa_feedback_pass_rate"),
    )

    qa_feedback_id = Column(BigInteger, primary_key=True, autoincrement=True)

    recording_log_id = Column(
        BigInteger, ForeignKey("recording_logs.recording_log_id"), nullable=False
    )
    qa_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)

    pass_rate = Column(Integer, nullable=False)
    feedback_text = Column(Text, nullable=False)
    is_rework_required = Column(Boolean, nullable=False, server_default="false", default=False)
    feedback_category = Column(FEEDBACK_CATEGORY_ENUM, nullable=False)

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

    recording_log = relationship("RecordingLog", foreign_keys=[recording_log_id])
    qa_user = relationship("User", foreign_keys=[qa_user_id])

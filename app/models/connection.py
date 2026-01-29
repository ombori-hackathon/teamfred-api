from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class IdeaConnection(Base):
    __tablename__ = "idea_connections"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(
        Integer, ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False
    )
    target_id = Column(
        Integer, ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False
    )
    label = Column(String(50), nullable=True)
    connection_type = Column(String(20), default="relates_to")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    source = relationship("Idea", foreign_keys=[source_id])
    target = relationship("Idea", foreign_keys=[target_id])

    __table_args__ = (
        CheckConstraint("source_id != target_id", name="check_no_self_connection"),
    )

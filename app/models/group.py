from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class IdeaGroup(Base):
    __tablename__ = "idea_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), default="#6b7280")
    board_id = Column(
        Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=True
    )
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    width = Column(Float, default=400.0)
    height = Column(Float, default=300.0)
    is_collapsed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    board = relationship("Board")
    ideas = relationship("Idea", back_populates="group")

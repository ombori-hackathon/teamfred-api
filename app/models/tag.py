from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base

# Junction table for many-to-many relationship between ideas and tags
idea_tags = Table(
    "idea_tags",
    Base.metadata,
    Column(
        "idea_id", Integer, ForeignKey("ideas.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), default="#6b7280")
    created_at = Column(DateTime, server_default=func.now())

    ideas = relationship("Idea", secondary=idea_tags, back_populates="tags")

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base
from app.models.tag import idea_tags


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    color = Column(String(20), default="yellow")
    position_x = Column(Float, default=100.0)
    position_y = Column(Float, default=100.0)
    width = Column(Float, default=200.0)
    height = Column(Float, default=150.0)
    rotation = Column(Float, default=0.0)
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # Board relationship
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True)
    board = relationship("Board", back_populates="ideas")

    # Tags relationship
    tags = relationship("Tag", secondary=idea_tags, back_populates="ideas")

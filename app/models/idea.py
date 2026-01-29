from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.db import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    color = Column(String(20), default="yellow")
    position_x = Column(Float, default=100.0)
    position_y = Column(Float, default=100.0)
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

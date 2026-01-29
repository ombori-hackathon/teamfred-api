from datetime import datetime

from pydantic import BaseModel


class IdeaBase(BaseModel):
    title: str
    description: str | None = None
    color: str = "yellow"


class IdeaCreate(IdeaBase):
    position_x: float = 100.0
    position_y: float = 100.0


class IdeaUpdatePosition(BaseModel):
    position_x: float
    position_y: float


class IdeaResponse(IdeaBase):
    id: int
    position_x: float
    position_y: float
    votes: int
    created_at: datetime

    class Config:
        from_attributes = True

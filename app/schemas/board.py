from datetime import datetime

from pydantic import BaseModel


class BoardBase(BaseModel):
    name: str
    description: str | None = None
    color: str = "#3b82f6"


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None


class BoardResponse(BoardBase):
    id: int
    created_at: datetime
    updated_at: datetime
    idea_count: int = 0

    class Config:
        from_attributes = True

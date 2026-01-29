from datetime import datetime

from pydantic import BaseModel

from app.schemas.tag import TagResponse


class IdeaBase(BaseModel):
    title: str
    description: str | None = None
    color: str = "yellow"


class IdeaCreate(IdeaBase):
    position_x: float = 100.0
    position_y: float = 100.0
    width: float = 200.0
    height: float = 150.0
    rotation: float = 0.0
    board_id: int | None = None
    tag_ids: list[int] = []


class IdeaUpdatePosition(BaseModel):
    position_x: float
    position_y: float


class IdeaUpdateSize(BaseModel):
    width: float
    height: float


class IdeaUpdateContent(BaseModel):
    title: str
    description: str | None = None


class IdeaUpdateTags(BaseModel):
    tag_ids: list[int]


class IdeaResponse(IdeaBase):
    id: int
    position_x: float
    position_y: float
    width: float
    height: float
    rotation: float
    votes: int
    created_at: datetime
    board_id: int | None = None
    group_id: int | None = None
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True

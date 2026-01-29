from datetime import datetime

from pydantic import BaseModel


class GroupBase(BaseModel):
    name: str
    color: str = "#6b7280"


class GroupCreate(GroupBase):
    board_id: int | None = None
    position_x: float = 0.0
    position_y: float = 0.0
    width: float = 400.0
    height: float = 300.0
    idea_ids: list[int] = []


class GroupUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    width: float | None = None
    height: float | None = None
    is_collapsed: bool | None = None


class GroupUpdatePosition(BaseModel):
    position_x: float
    position_y: float


class GroupUpdateSize(BaseModel):
    width: float
    height: float


class GroupAddIdeas(BaseModel):
    idea_ids: list[int]


class GroupResponse(GroupBase):
    id: int
    board_id: int | None
    position_x: float
    position_y: float
    width: float
    height: float
    is_collapsed: bool
    created_at: datetime
    idea_ids: list[int] = []

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.group import IdeaGroup
from app.models.idea import Idea
from app.schemas.group import (
    GroupAddIdeas,
    GroupCreate,
    GroupResponse,
    GroupUpdate,
    GroupUpdatePosition,
    GroupUpdateSize,
)

router = APIRouter(prefix="/groups", tags=["groups"])


def group_to_response(group: IdeaGroup) -> GroupResponse:
    """Convert group model to response with idea_ids"""
    return GroupResponse(
        id=group.id,
        name=group.name,
        color=group.color,
        board_id=group.board_id,
        position_x=group.position_x,
        position_y=group.position_y,
        width=group.width,
        height=group.height,
        is_collapsed=group.is_collapsed,
        created_at=group.created_at,
        idea_ids=[idea.id for idea in group.ideas],
    )


@router.get("", response_model=list[GroupResponse])
async def get_groups(
    board_id: int | None = Query(None, description="Filter by board ID"),
    db: Session = Depends(get_db),
):
    """Get all groups, optionally filtered by board"""
    query = db.query(IdeaGroup)

    if board_id is not None:
        query = query.filter(IdeaGroup.board_id == board_id)

    groups = query.order_by(IdeaGroup.created_at).all()
    return [group_to_response(g) for g in groups]


@router.post("", response_model=GroupResponse)
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """Create a new group with optional initial ideas"""
    db_group = IdeaGroup(
        name=group.name,
        color=group.color,
        board_id=group.board_id,
        position_x=group.position_x,
        position_y=group.position_y,
        width=group.width,
        height=group.height,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    # Add ideas to group if specified
    if group.idea_ids:
        ideas = db.query(Idea).filter(Idea.id.in_(group.idea_ids)).all()
        for idea in ideas:
            idea.group_id = db_group.id
        db.commit()
        db.refresh(db_group)

    return group_to_response(db_group)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get a specific group by ID"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group_to_response(group)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int, update: GroupUpdate, db: Session = Depends(get_db)
):
    """Update a group's properties"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if update.name is not None:
        group.name = update.name
    if update.color is not None:
        group.color = update.color
    if update.position_x is not None:
        group.position_x = update.position_x
    if update.position_y is not None:
        group.position_y = update.position_y
    if update.width is not None:
        group.width = update.width
    if update.height is not None:
        group.height = update.height
    if update.is_collapsed is not None:
        group.is_collapsed = update.is_collapsed

    db.commit()
    db.refresh(group)
    return group_to_response(group)


@router.patch("/{group_id}/position", response_model=GroupResponse)
async def update_group_position(
    group_id: int, position: GroupUpdatePosition, db: Session = Depends(get_db)
):
    """Update group position after drag"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group.position_x = position.position_x
    group.position_y = position.position_y
    db.commit()
    db.refresh(group)
    return group_to_response(group)


@router.patch("/{group_id}/size", response_model=GroupResponse)
async def update_group_size(
    group_id: int, size: GroupUpdateSize, db: Session = Depends(get_db)
):
    """Update group size after resize"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group.width = size.width
    group.height = size.height
    db.commit()
    db.refresh(group)
    return group_to_response(group)


@router.post("/{group_id}/ideas", response_model=GroupResponse)
async def add_ideas_to_group(
    group_id: int, ideas_update: GroupAddIdeas, db: Session = Depends(get_db)
):
    """Add ideas to a group"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    ideas = db.query(Idea).filter(Idea.id.in_(ideas_update.idea_ids)).all()
    for idea in ideas:
        idea.group_id = group_id

    db.commit()
    db.refresh(group)
    return group_to_response(group)


@router.delete("/{group_id}/ideas/{idea_id}", response_model=GroupResponse)
async def remove_idea_from_group(
    group_id: int, idea_id: int, db: Session = Depends(get_db)
):
    """Remove an idea from a group"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    idea = db.query(Idea).filter(Idea.id == idea_id, Idea.group_id == group_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found in this group")

    idea.group_id = None
    db.commit()
    db.refresh(group)
    return group_to_response(group)


@router.delete("/{group_id}")
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Delete a group (ideas are kept but unassigned)"""
    group = db.query(IdeaGroup).filter(IdeaGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Unassign ideas from group
    for idea in group.ideas:
        idea.group_id = None

    db.delete(group)
    db.commit()
    return {"message": "Group deleted"}

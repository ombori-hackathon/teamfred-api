from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models.idea import Idea
from app.models.tag import Tag
from app.schemas.idea import (
    IdeaCreate,
    IdeaResponse,
    IdeaUpdateContent,
    IdeaUpdatePosition,
    IdeaUpdateSize,
    IdeaUpdateTags,
)

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get("", response_model=list[IdeaResponse])
async def get_ideas(
    board_id: int | None = Query(None, description="Filter by board ID"),
    tag_ids: list[int] | None = Query(None, description="Filter by tag IDs"),
    db: Session = Depends(get_db),
):
    """Get all ideas, optionally filtered by board and/or tags"""
    query = db.query(Idea).options(joinedload(Idea.tags))

    if board_id is not None:
        query = query.filter(Idea.board_id == board_id)

    if tag_ids:
        # Filter ideas that have ALL specified tags
        for tag_id in tag_ids:
            query = query.filter(Idea.tags.any(Tag.id == tag_id))

    return query.order_by(Idea.created_at).all()


@router.post("", response_model=IdeaResponse)
async def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    """Create a new idea"""
    db_idea = Idea(
        title=idea.title,
        description=idea.description,
        color=idea.color,
        position_x=idea.position_x,
        position_y=idea.position_y,
        width=idea.width,
        height=idea.height,
        rotation=idea.rotation,
        board_id=idea.board_id,
    )

    # Add tags if specified
    if idea.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(idea.tag_ids)).all()
        db_idea.tags = tags

    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


@router.patch("/{idea_id}/position", response_model=IdeaResponse)
async def update_idea_position(
    idea_id: int, position: IdeaUpdatePosition, db: Session = Depends(get_db)
):
    """Update idea position after drag"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.position_x = position.position_x
    idea.position_y = position.position_y
    db.commit()
    db.refresh(idea)
    return idea


@router.patch("/{idea_id}/size", response_model=IdeaResponse)
async def update_idea_size(
    idea_id: int, size: IdeaUpdateSize, db: Session = Depends(get_db)
):
    """Update idea size after resize"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.width = size.width
    idea.height = size.height
    db.commit()
    db.refresh(idea)
    return idea


@router.patch("/{idea_id}/content", response_model=IdeaResponse)
async def update_idea_content(
    idea_id: int, content: IdeaUpdateContent, db: Session = Depends(get_db)
):
    """Update idea title and description"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.title = content.title
    idea.description = content.description
    db.commit()
    db.refresh(idea)
    return idea


@router.post("/{idea_id}/vote", response_model=IdeaResponse)
async def vote_idea(idea_id: int, db: Session = Depends(get_db)):
    """Increment vote count for an idea"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.votes += 1
    db.commit()
    db.refresh(idea)
    return idea


@router.delete("/{idea_id}")
async def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    """Delete an idea"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(idea)
    db.commit()
    return {"message": "Idea deleted"}


@router.patch("/{idea_id}/tags", response_model=IdeaResponse)
async def update_idea_tags(
    idea_id: int, tags_update: IdeaUpdateTags, db: Session = Depends(get_db)
):
    """Update idea's tags"""
    idea = (
        db.query(Idea).options(joinedload(Idea.tags)).filter(Idea.id == idea_id).first()
    )
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Replace tags with new ones
    tags = db.query(Tag).filter(Tag.id.in_(tags_update.tag_ids)).all()
    idea.tags = tags

    db.commit()
    db.refresh(idea)
    return idea

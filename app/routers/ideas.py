from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaResponse, IdeaUpdatePosition

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get("", response_model=list[IdeaResponse])
async def get_ideas(db: Session = Depends(get_db)):
    """Get all ideas"""
    return db.query(Idea).order_by(Idea.created_at).all()


@router.post("", response_model=IdeaResponse)
async def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    """Create a new idea"""
    db_idea = Idea(
        title=idea.title,
        description=idea.description,
        color=idea.color,
        position_x=idea.position_x,
        position_y=idea.position_y,
    )
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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def get_tags(db: Session = Depends(get_db)):
    """Get all tags"""
    return db.query(Tag).order_by(Tag.name).all()


@router.post("", response_model=TagResponse)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag"""
    # Check if tag with same name already exists
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")

    db_tag = Tag(
        name=tag.name,
        color=tag.color,
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted"}

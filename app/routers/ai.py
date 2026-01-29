from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.board import Board
from app.models.tag import Tag
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


class SuggestionsRequest(BaseModel):
    board_id: int


class SuggestionsResponse(BaseModel):
    suggestions: list[str]


class SummarizeRequest(BaseModel):
    board_id: int


class SummarizeResponse(BaseModel):
    summary: str
    themes: list[str]
    top_priority: str | None


class CategorizeRequest(BaseModel):
    title: str
    description: str | None = None


class CategorizeResponse(BaseModel):
    suggested_tags: list[str]


def check_api_key():
    """Check if API key is configured"""
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI features not available. ANTHROPIC_API_KEY not configured.",
        )


@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(request: SuggestionsRequest, db: Session = Depends(get_db)):
    """Generate idea suggestions for a board"""
    check_api_key()

    board = db.query(Board).filter(Board.id == request.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    existing_ideas = [
        {"title": idea.title, "description": idea.description} for idea in board.ideas
    ]

    try:
        suggestions = ai_service.get_idea_suggestions(board.name, existing_ideas)
        return SuggestionsResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_board(request: SummarizeRequest, db: Session = Depends(get_db)):
    """Summarize a board's ideas"""
    check_api_key()

    board = db.query(Board).filter(Board.id == request.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    ideas = [
        {"title": idea.title, "description": idea.description, "votes": idea.votes}
        for idea in board.ideas
    ]

    try:
        result = ai_service.summarize_board(board.name, ideas)
        return SummarizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_idea(request: CategorizeRequest, db: Session = Depends(get_db)):
    """Auto-suggest tags for an idea"""
    check_api_key()

    existing_tags = [tag.name for tag in db.query(Tag).all()]

    try:
        suggestions = ai_service.auto_categorize_idea(
            request.title, request.description, existing_tags
        )
        return CategorizeResponse(suggested_tags=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

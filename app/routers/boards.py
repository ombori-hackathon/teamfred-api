from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardResponse, BoardUpdate

router = APIRouter(prefix="/boards", tags=["boards"])


def board_to_response(board: Board) -> dict:
    """Convert board model to response with idea_count"""
    return {
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "color": board.color,
        "created_at": board.created_at,
        "updated_at": board.updated_at,
        "idea_count": len(board.ideas),
    }


@router.get("", response_model=list[BoardResponse])
async def get_boards(db: Session = Depends(get_db)):
    """Get all boards with idea counts"""
    boards = db.query(Board).order_by(Board.created_at).all()
    return [board_to_response(board) for board in boards]


@router.post("", response_model=BoardResponse)
async def create_board(board: BoardCreate, db: Session = Depends(get_db)):
    """Create a new board"""
    db_board = Board(
        name=board.name,
        description=board.description,
        color=board.color,
    )
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return board_to_response(db_board)


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(board_id: int, db: Session = Depends(get_db)):
    """Get a specific board by ID"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board_to_response(board)


@router.patch("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int, board_update: BoardUpdate, db: Session = Depends(get_db)
):
    """Update a board"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if board_update.name is not None:
        board.name = board_update.name
    if board_update.description is not None:
        board.description = board_update.description
    if board_update.color is not None:
        board.color = board_update.color

    db.commit()
    db.refresh(board)
    return board_to_response(board)


@router.delete("/{board_id}")
async def delete_board(board_id: int, db: Session = Depends(get_db)):
    """Delete a board and all its ideas"""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    db.delete(board)
    db.commit()
    return {"message": "Board deleted"}

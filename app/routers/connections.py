from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.connection import IdeaConnection
from app.models.idea import Idea
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
)

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get("", response_model=list[ConnectionResponse])
async def get_connections(
    board_id: int | None = Query(
        None, description="Filter by board ID (via source idea)"
    ),
    db: Session = Depends(get_db),
):
    """Get all connections, optionally filtered by board"""
    query = db.query(IdeaConnection)

    if board_id is not None:
        # Filter connections where source idea belongs to the board
        query = query.join(Idea, IdeaConnection.source_id == Idea.id).filter(
            Idea.board_id == board_id
        )

    return query.order_by(IdeaConnection.created_at).all()


@router.post("", response_model=ConnectionResponse)
async def create_connection(
    connection: ConnectionCreate, db: Session = Depends(get_db)
):
    """Create a new connection between two ideas"""
    # Verify source and target ideas exist
    source = db.query(Idea).filter(Idea.id == connection.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source idea not found")

    target = db.query(Idea).filter(Idea.id == connection.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target idea not found")

    # Check if connection already exists
    existing = (
        db.query(IdeaConnection)
        .filter(
            IdeaConnection.source_id == connection.source_id,
            IdeaConnection.target_id == connection.target_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Connection between these ideas already exists"
        )

    db_connection = IdeaConnection(
        source_id=connection.source_id,
        target_id=connection.target_id,
        label=connection.label,
        connection_type=connection.connection_type,
    )

    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(connection_id: int, db: Session = Depends(get_db)):
    """Get a specific connection by ID"""
    connection = (
        db.query(IdeaConnection).filter(IdeaConnection.id == connection_id).first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connection


@router.patch("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: int, update: ConnectionUpdate, db: Session = Depends(get_db)
):
    """Update a connection's label or type"""
    connection = (
        db.query(IdeaConnection).filter(IdeaConnection.id == connection_id).first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if update.label is not None:
        connection.label = update.label
    if update.connection_type is not None:
        connection.connection_type = update.connection_type

    db.commit()
    db.refresh(connection)
    return connection


@router.delete("/{connection_id}")
async def delete_connection(connection_id: int, db: Session = Depends(get_db)):
    """Delete a connection"""
    connection = (
        db.query(IdeaConnection).filter(IdeaConnection.id == connection_id).first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    db.delete(connection)
    db.commit()
    return {"message": "Connection deleted"}

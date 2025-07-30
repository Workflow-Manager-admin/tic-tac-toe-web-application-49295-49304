from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
from typing import Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- User CRUD ---

# PUBLIC_INTERFACE
def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Fetch a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

# PUBLIC_INTERFACE
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Fetch a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

# PUBLIC_INTERFACE
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with hashed password."""
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Game CRUD ---

# PUBLIC_INTERFACE
def create_game(db: Session, owner_id: int, opponent_id: Optional[int] = None) -> models.Game:
    """Create a new game with owner and optional opponent."""
    db_game = models.Game(owner_id=owner_id, opponent_id=opponent_id)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# PUBLIC_INTERFACE
def get_game(db: Session, game_id: int) -> Optional[models.Game]:
    """Fetch game by ID."""
    return db.query(models.Game).filter(models.Game.id == game_id).first()

# PUBLIC_INTERFACE
def list_games_for_user(db: Session, user_id: int):
    """List all games for a user (as owner or opponent)."""
    return db.query(models.Game).filter(
        or_(models.Game.owner_id == user_id, models.Game.opponent_id == user_id)
    ).all()

# --- Move CRUD ---

# PUBLIC_INTERFACE
def add_move(
    db: Session, game_id: int, move: schemas.MoveCreate
) -> models.Move:
    """Record a move in a given game."""
    db_move = models.Move(
        game_id=game_id,
        player_id=move.player_id,
        row=move.row,
        col=move.col,
        symbol=move.symbol,
        turn_number=move.turn_number,
    )
    db.add(db_move)
    db.commit()
    db.refresh(db_move)
    return db_move

# PUBLIC_INTERFACE
def list_moves_for_game(db: Session, game_id: int):
    """Get all moves for the specified game."""
    return db.query(models.Move).filter(models.Move.game_id == game_id).order_by(models.Move.turn_number).all()

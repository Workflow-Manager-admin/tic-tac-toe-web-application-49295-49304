from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum
import datetime

Base = declarative_base()

class GameStatus(str, enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# PUBLIC_INTERFACE
class User(Base):
    """Represents a registered user/player."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    games = relationship("Game", back_populates="owner", foreign_keys="[Game.owner_id]")

# PUBLIC_INTERFACE
class Game(Base):
    """Represents a Tic Tac Toe game."""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    opponent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(GameStatus), default=GameStatus.WAITING)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="games")
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")

# PUBLIC_INTERFACE
class Move(Base):
    """Represents a move in a game."""
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("users.id"))
    row = Column(Integer, nullable=False)
    col = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)  # 'X' or 'O'
    turn_number = Column(Integer, nullable=False)
    played_at = Column(DateTime, default=datetime.datetime.utcnow)

    game = relationship("Game", back_populates="moves")

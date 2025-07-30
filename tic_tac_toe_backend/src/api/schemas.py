from pydantic import BaseModel, Field
from typing import Optional
import datetime
from enum import Enum

# PUBLIC_INTERFACE
class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# --- User Schemas ---

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    username: str = Field(..., description="User's unique username")

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    password: str = Field(..., description="Plain-text password for user registration")

# PUBLIC_INTERFACE
class UserOut(UserBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# --- Game Schemas ---

# PUBLIC_INTERFACE
class GameBase(BaseModel):
    status: Optional[GameStatus] = Field(default=GameStatus.WAITING, description="Current game status")

# PUBLIC_INTERFACE
class GameCreate(BaseModel):
    opponent_id: Optional[int] = Field(default=None, description="Optional opponent user id")

# PUBLIC_INTERFACE
class GameOut(GameBase):
    id: int
    owner_id: int
    opponent_id: Optional[int]
    winner_id: Optional[int]
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# --- Move Schemas ---

# PUBLIC_INTERFACE
class MoveBase(BaseModel):
    row: int = Field(..., ge=0, le=2, description="Row position (0-2)")
    col: int = Field(..., ge=0, le=2, description="Column position (0-2)")
    symbol: str = Field(..., regex="^[XO]$", description="Move symbol: X or O")

# PUBLIC_INTERFACE
class MoveCreate(MoveBase):
    player_id: int
    turn_number: int

# PUBLIC_INTERFACE
class MoveOut(MoveBase):
    id: int
    game_id: int
    player_id: int
    turn_number: int
    played_at: datetime.datetime

    class Config:
        orm_mode = True

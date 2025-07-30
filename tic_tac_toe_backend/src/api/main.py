from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Import database setup and models to ensure DB tables are created
from . import database

from .auth import router as auth_router, get_current_user
from . import crud, schemas, models

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from .database import get_db

app = FastAPI(
    title="Tic Tac Toe Backend API",
    description="Handles authentication, games, moves, and user data for Tic Tac Toe.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication endpoints
app.include_router(auth_router)

@app.on_event("startup")
def on_startup():
    """
    Create database tables at startup if not exist.
    """
    database.init_db()

@app.get("/", tags=["Health"])
def health_check():
    """Returns backend health status."""
    return {"message": "Healthy"}

# --- PROTECTED ENDPOINTS (sample implementation for Game & Move) --- #

game_router = APIRouter(prefix="/games", tags=["Games"])

# PUBLIC_INTERFACE
@game_router.post("/", response_model=schemas.GameOut)
def create_game(
    game: schemas.GameCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new game. Must be authenticated."""
    db_game = crud.create_game(db, owner_id=current_user.id, opponent_id=game.opponent_id)
    return db_game

# PUBLIC_INTERFACE
@game_router.get("/", response_model=list[schemas.GameOut])
def list_my_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all games for yourself (as owner or opponent)."""
    games = crud.list_games_for_user(db, user_id=current_user.id)
    return games

# PUBLIC_INTERFACE
@game_router.get("/{game_id}", response_model=schemas.GameOut)
def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get game details by id (auth required)."""
    game = crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if (game.owner_id != current_user.id) and (game.opponent_id != current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden")
    return game

move_router = APIRouter(prefix="/moves", tags=["Moves"])

# PUBLIC_INTERFACE
@move_router.post("/{game_id}", response_model=schemas.MoveOut)
def make_move(
    game_id: int,
    move: schemas.MoveCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Record a move for a game (auth required)."""
    game = crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # Only owner or opponent can play
    if move.player_id != current_user.id or (current_user.id != game.owner_id and current_user.id != game.opponent_id):
        raise HTTPException(status_code=403, detail="You can't play in this game")
    db_move = crud.add_move(db, game_id=game_id, move=move)
    return db_move

# PUBLIC_INTERFACE
@move_router.get("/by_game/{game_id}", response_model=list[schemas.MoveOut])
def get_moves(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all moves for a game (auth required)."""
    game = crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if (game.owner_id != current_user.id) and (game.opponent_id != current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden")
    moves = crud.list_moves_for_game(db, game_id)
    return moves

app.include_router(game_router)
app.include_router(move_router)

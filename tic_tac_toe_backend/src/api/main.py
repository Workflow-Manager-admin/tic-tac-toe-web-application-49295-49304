from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database setup and models to ensure DB tables are created
from . import database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    Create database tables at startup if not exist.
    """
    database.init_db()

@app.get("/")
def health_check():
    """Returns backend health status."""
    return {"message": "Healthy"}

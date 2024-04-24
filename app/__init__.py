from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy_utils import create_database, database_exists
from app.routers import users
from app.utils.database import Base, engine

def create_app():
    app = FastAPI(
        title="Template FastAPI Server",
        description="A sample API for universal template.",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(users.router, prefix="/api", tags=["users"])

    # Create database tables
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    return app

app = create_app()
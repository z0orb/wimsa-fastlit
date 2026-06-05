from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_defaults()
    yield


def _seed_defaults():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            db.add(
                User(
                    username="admin",
                    email="admin@wimsa.local",
                    hashed_password=hash_password("admin123"),
                    role="supervisor",
                )
            )
        existing = db.query(User).filter(User.username == "staff").first()
        if not existing:
            db.add(
                User(
                    username="staff",
                    email="staff@wimsa.local",
                    hashed_password=hash_password("staff123"),
                    role="ground_staff",
                )
            )
        db.commit()
    finally:
        db.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router)
    return app


app = create_app()

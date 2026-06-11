from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.chat import router as chat_router
from app.api.recommend import router as recommend_router
from app.api.travel import router as travel_router
from app.core.config import settings
from app.core.database import Base, engine


def ensure_schema_compat() -> None:
    inspector = inspect(engine)
    if "travel_records" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("travel_records")}
    dialect = engine.dialect.name
    if dialect == "mysql":
        additions = {
            "source_type": "ADD COLUMN source_type VARCHAR(20) NOT NULL DEFAULT 'form'",
            "chat_session_id": "ADD COLUMN chat_session_id VARCHAR(80) NULL",
            "image_urls": "ADD COLUMN image_urls JSON NULL",
            "hand_account_layout": "ADD COLUMN hand_account_layout JSON NULL",
            "exported_long_image_url": "ADD COLUMN exported_long_image_url VARCHAR(255) NULL",
        }
    else:
        additions = {
            "source_type": "ADD COLUMN source_type VARCHAR(20) NOT NULL DEFAULT 'form'",
            "chat_session_id": "ADD COLUMN chat_session_id VARCHAR(80)",
            "image_urls": "ADD COLUMN image_urls JSON",
            "hand_account_layout": "ADD COLUMN hand_account_layout JSON",
            "exported_long_image_url": "ADD COLUMN exported_long_image_url VARCHAR(255)",
        }

    with engine.begin() as conn:
        for column, ddl in additions.items():
            if column not in existing:
                conn.execute(text(f"ALTER TABLE travel_records {ddl}"))


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        ensure_schema_compat()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    app.include_router(travel_router, prefix="/api/travel", tags=["travel"])
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    app.include_router(recommend_router, prefix="/api/recommend", tags=["recommend"])
    return app


app = create_app()

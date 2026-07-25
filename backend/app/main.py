from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import health, citizens, schemes, reminders, assistant, webhook
from app.seed import seed_database
import app.models  # Ensures all models are registered with Base


def create_app() -> FastAPI:
    # Auto-create SQLite tables
    Base.metadata.create_all(bind=engine)

    # Seed Database on Startup if empty
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="JanSathi AI - Public Assistance & Citizen Services API",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core API Routers
    app.include_router(health.router, prefix=settings.API_PREFIX)
    app.include_router(citizens.router, prefix=f"{settings.API_PREFIX}/api")
    app.include_router(schemes.router, prefix=f"{settings.API_PREFIX}/api")
    app.include_router(reminders.router, prefix=f"{settings.API_PREFIX}/api")
    app.include_router(assistant.router, prefix=f"{settings.API_PREFIX}/api")

    # WhatsApp Webhook (mounted at root /webhook for Meta verification compatibility)
    app.include_router(webhook.router, prefix=settings.API_PREFIX)

    return app


app = create_app()

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import health, citizens, schemes, reminders, assistant, webhook
from app.seed import seed_database
import app.models  # Ensures all models are registered with Base

logger = logging.getLogger("jansathi")


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
        description=(
            "JanSathi AI - Public Assistance & Citizen Services API\n\n"
            "Integrates: SQLite database, Sarvam AI reasoning, and Twilio WhatsApp Sandbox."
        ),
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

    # Root API Welcome Endpoint
    @app.get("/", tags=["Root"])
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "documentation": "/docs",
            "health_check": "/health"
        }

    # Core API Routers
    app.include_router(health.router, prefix=settings.API_PREFIX)
    app.include_router(citizens.router, prefix=f"{settings.API_PREFIX}/api")
    app.include_router(schemes.router, prefix=f"{settings.API_PREFIX}/api")
    app.include_router(reminders.router, prefix=f"{settings.API_PREFIX}/api")
    app.include_router(assistant.router, prefix=f"{settings.API_PREFIX}/api")

    # Twilio WhatsApp Webhook (mounted at /webhook)
    app.include_router(webhook.router, prefix=settings.API_PREFIX)

    @app.on_event("startup")
    async def startup_log():
        import asyncio
        from app.services.twilio_whatsapp_service import twilio_whatsapp_service
        from app.services.sarvam_service import sarvam_client
        from app.services.gemini_service import gemini_rag_service
        from app.services.scheduler import start_daily_scheme_scheduler

        # Start daily scheme ingestion scheduler loop in background
        asyncio.create_task(start_daily_scheme_scheduler())

        logger.info(f"[JanSathi AI] ✅ Server started: {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"[JanSathi AI] 🤖 Gemini RAG Engine: {'✅ Configured' if gemini_rag_service.is_configured() else '⚠️  Not configured (using grounded fallback reasoning)'}")
        logger.info(f"[JanSathi AI] 🤖 Sarvam AI (General Chat): {'✅ Configured' if sarvam_client.is_configured() else '⚠️  Not configured'}")
        logger.info(f"[JanSathi AI] 🔄 Daily Scheme Auto-Sync Scheduler: ✅ Active (24h Loop)")
        logger.info(f"[JanSathi AI] 📱 Twilio WhatsApp Sandbox: {'✅ Configured' if twilio_whatsapp_service.is_configured() else '⚠️  Not configured (web app unaffected)'}")
        if twilio_whatsapp_service.is_configured():
            logger.info(f"[JanSathi AI] 📞 Twilio WhatsApp Number: {twilio_whatsapp_service.from_number}")

    return app


app = create_app()

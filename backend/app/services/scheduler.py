import asyncio
import logging
from app.database import SessionLocal
from app.services.scheme_collector import scheme_collector

logger = logging.getLogger("jansathi.scheduler")

IS_RUNNING = False


async def start_daily_scheme_scheduler():
    """
    Asynchronous background task runner that executes daily government scheme ingestion every 24 hours.
    """
    global IS_RUNNING
    if IS_RUNNING:
        return
    IS_RUNNING = True
    logger.info("[Scheduler] Starting automated daily government scheme ingestion background task...")

    while True:
        try:
            db = SessionLocal()
            try:
                res = scheme_collector.sync_latest_schemes(db)
                logger.info(f"[Scheduler Sync] Status: {res['status']} | Added: {res['new_schemes_added']} | Total DB: {res['total_schemes_in_db']}")
            finally:
                db.close()
        except Exception as err:
            logger.error(f"[Scheduler Error] Exception during daily scheme sync: {err}")

        # Sleep for 24 Hours (86,400 seconds) between automated daily syncs
        await asyncio.sleep(86400)

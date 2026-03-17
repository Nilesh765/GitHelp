import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, engine
from sqlalchemy import text
from app.core.cache import redis_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

@router.get("/live")
def liveness():
    return {"status": "ok"}

@router.get("/ready")
async def readiness():
    checks = {}
    all_healthy = True

    try:
        async with AsyncSession(engine) as db:
            await db.execute(text("SELECT 1"))
            checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "detail": str(e)}
        all_healthy = False
        logger.error("Database health check failed", extra={"error": str(e)})

    redis_ok = await ping_redis()
    if redis_ok:
        checks["redis"] = {"status": "ok"}
    else:
        checks["redis"] = {"status": "error", "detail": "Redis health check failed"}
        all_healthy = False
        logger.error("Redis health check failed")

    status_code = 200 if all_healthy else 503
    return JSONResponse(status_code=status_code, content={
        "status": "ok" if all_healthy else "degraded",
        "checks": checks
    })
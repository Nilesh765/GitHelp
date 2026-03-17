from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from app.core.logger import setup_logging

setup_logging()

from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.user.router import router as user_router
from app.modules.repository.router import router as repository_router
from app.modules.task.router import router as task_router
from app.modules.review.router import router as review_router
from app.api.health import router as health_router
from app.core.middleware import CorrelationIDMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("GitHelp API starting", extra={"version": "0.1.0"})
    yield
    logger.info("GitHelp API shutdown")

app = FastAPI(
    title="GitHelp",
    description="AI-Powered Code Review Assistant",
    version="0.1.0",
    lifespan=lifespan
)


app.add_middleware(CorrelationIDMiddleware)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(repository_router)
app.include_router(task_router)
app.include_router(review_router)
app.include_router(health_router)
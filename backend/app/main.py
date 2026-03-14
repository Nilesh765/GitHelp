from fastapi import FastAPI
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.repositories.router import router as repositories_router
from app.modules.tasks.router import router as tasks_router
from app.modules.reviews.router import router as reviews_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GitHelp API"
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(repositories_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")

@app.get("/health/live", tags=["Health"])
async def health_live():
    return {"status": "ok", "message": "GitHelp is alive and kicking"}
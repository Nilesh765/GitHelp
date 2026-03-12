from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GitHelp API"
)

@app.get("/health/live", tags=["Health"])
async def health_live():
    return {"status": "ok", "message": "GitHelp is alive and kicking"}
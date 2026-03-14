import uuid
import asyncio
from app.modules.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.modules.repositories.models import Repository
from app.modules.reviews.models import Review
from app.common.enums import RepoStatus, ReviewStatus

async def _run_analysis_async(repository_id: str, celery_task):
    """The actual async database work."""
    async with AsyncSessionLocal() as db:
        # 1. Fetch the repository
        repo = await db.get(Repository, uuid.UUID(repository_id))
        if not repo:
            return {"status": "error", "message": "Repository not found"}

        # 2. Mark repo as analyzing
        repo.status = RepoStatus.analyzing
        await db.commit()

        review = Review(
            repository_id=repo.id, 
            status=ReviewStatus.in_progress
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Update Flower UI via the injected celery_task
        celery_task.update_state(state="STARTED", meta={"progress": 25, "stage": "cloning repository"})
        await asyncio.sleep(3) # Use async sleep here!

        celery_task.update_state(state="STARTED", meta={"progress": 50, "stage": "running AI analysis"})
        await asyncio.sleep(3)

        celery_task.update_state(state="STARTED", meta={"progress": 90, "stage": "saving results"})

        # 4. The AI finished! Update the Review
        review.status = ReviewStatus.completed
        review.quality_score = 75
        review.security_score = 80
        review.maintainability_score = 60
        review.summary = "This is a dummy AI review summary."
        
        # 5. Mark the Repository as completed
        repo.status = RepoStatus.completed
        await db.commit()

        return {"status": "completed", "repository_id": repository_id, "review_id": str(review.id)}

# 2. THE SYNCHRONOUS CELERY WRAPPER
# This is the function Celery actually calls. It is completely sync.
@celery_app.task(bind=True, max_retries=3)
def analyze_repository(self, repository_id: str):
    # We use asyncio.run() to bridge the sync Celery worker to our async database function!
    # We pass 'self' in so the inner function can still update the Flower UI.
    return asyncio.run(_run_analysis_async(repository_id, self))
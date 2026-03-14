import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.reviews.models import Review
from app.modules.reviews.schemas import ReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch the results of an AI analysis."""
    
    review = await db.get(Review, review_id)
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found. Are you sure the ID is correct?")
        
    return review
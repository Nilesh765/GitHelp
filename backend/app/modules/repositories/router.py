from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.common.enums import RepoProvider, RepoStatus
from app.modules.repositories.models import Repository
from app.modules.repositories import service as repo_service
from app.modules.repositories.schemas import (
    RepoSubmitRequest,
    RepoResponse,
    RepoUpdateRequest,
    RepoSummaryResponse,
    TaskStatusResponse
)
from app.modules.tasks.analysis_tasks import analyze_repository

router = APIRouter(prefix="/repo", tags=["Repositories"])

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def submit_repository(
    request: RepoSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await repo_service.create_repository(current_user.id, request, db)
    return {
        "message": "Repository submitted for analysis",
        "repository_id": str(result["repository_id"]),
        "task_id": result["task_id"]
    }

@router.get("/", response_model=list[RepoSummaryResponse])
async def list_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all repositories for the current user.
    """
    return await repo_service.list_repositories(db, current_user)

@router.get("/{repo_id}", response_model=RepoResponse)
async def get_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific repository.
    """
    return await repo_service.get_repository(db, repo_id, current_user)

@router.patch("/{repo_id}", response_model=RepoResponse)
async def update_repository(
    repo_id: UUID,
    repo_update: RepoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a repository configuration.
    """
    return await repo_service.update_repository(db, repo_id, current_user, repo_update)

@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a repository.
    """
    await repo_service.delete_repository(db, repo_id, current_user)
    return None

@router.post("/{repo_id}/reanalyze", status_code=status.HTTP_202_ACCEPTED)
async def reanalyze_repository(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger re-analysis of a repository.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Pending"
    )

@router.get("/{repo_id}/history")
async def get_repository_history(
    repo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analysis history of a repository.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Pending"
    )
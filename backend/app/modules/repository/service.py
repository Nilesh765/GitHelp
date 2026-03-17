import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from fastapi import HTTPException, status
from app.modules.task.analysis_task import analyze_repository
from app.modules.user.model import User
from app.common.enums import RepoProvider, RepoStatus
from app.modules.repository.model import Repository
from app.modules.repository.schema import RepoSubmitRequest, RepoUpdateRequest


async def create_repository(owner_id: uuid.UUID, request: RepoSubmitRequest, db: AsyncSession) -> dict:
    provider_enum = RepoProvider.github if "github.com" in request.url else RepoProvider.gitlab

    new_repo = Repository(
        owner_id=owner_id,
        url=request.url,
        provider=provider_enum,
        is_private=request.is_private,
        default_branch=request.default_branch,
        analysis_config=request.analysis_config,
        status=RepoStatus.pending,
    )

    db.add(new_repo)
    await db.commit()
    await db.refresh(new_repo)

    return new_repo

async def list_repositories(db: AsyncSession, user: User) -> list[Repository]:
    query = select(Repository).where(Repository.owner_id == user.id)
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_repository(db: AsyncSession, repo_id: UUID, user: User) -> Repository:
    query = select(Repository).where(Repository.id == repo_id, Repository.owner_id == user.id)
    result = await db.execute(query)
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo

async def update_repository(db: AsyncSession, repo_id: UUID, user: User, repo_update: RepoUpdateRequest) -> Repository:
    repo = await get_repository(db, repo_id, user)
    if repo_update.default_branch:
        repo.default_branch = repo_update.default_branch
    if repo_update.analysis_config:
        repo.analysis_config = repo_update.analysis_config
    
    await db.commit()
    await db.refresh(repo)
    return repo

async def update_repository_status(db: AsyncSession, repo_id: UUID, user: User, status: RepoStatus, celery_task_id: str | None = None, error_message: str | None = None) -> Repository:
    result = await db.execute(select(Repository).where(Repository.id == repo_id, Repository.owner_id == user.id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    repo.status = status
    await db.commit()
    await db.refresh(repo)
    return repo

async def delete_repository(db: AsyncSession, repo_id: UUID, user: User) -> None:
    repo = await get_repository(db, repo_id, user)
    await db.delete(repo)
    await db.commit()


from fastapi import APIRouter
from celery.result import AsyncResult

from app.modules.repository.schema import TaskStatusResponse
from app.modules.task.celery_app import celery_app

router = APIRouter(tags=["Tasks"])

@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):

    task = AsyncResult(task_id, app=celery_app)

    state= task.state
    progress = 0
    stage = ""
    result = None
    error = None

    if state == "STARTED":
        progress = task.info.get("progress", 0) if task.info else 0
        stage = task.info.get("stage", "") if task.info else ""
    elif state == "SUCCESS":
        progress = 100
        stage = "Complete"
        result = task.result
    elif state == "FAILURE":
        stage = "Failed"
        error = str(task.info)
    
    return {
        "task_id": task_id,
        "status": state,
        "progress": progress,
        "stage": stage,
        "result": result,
        "error": error
    }

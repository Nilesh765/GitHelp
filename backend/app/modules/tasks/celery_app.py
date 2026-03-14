from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "githelp",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.modules.tasks.analysis_tasks"
    ]
)

celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

celery_app.conf.task_routes = {
    "app.modules.tasks.analysis_tasks.*": {"queue": "analysis"},
}
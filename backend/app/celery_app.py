"""
Celery application configuration for background task processing.

Provides async task execution for long-running ML operations.
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "pharma_ai_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.drug_design_tasks",
        "app.tasks.clinical_trials_tasks",
        "app.tasks.safety_tasks",
        "app.tasks.repurposing_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # Results expire after 24 hours
    broker_connection_retry_on_startup=True,
)

# Task routes
celery_app.conf.task_routes = {
    "app.tasks.drug_design_tasks.*": {"queue": "drug_design"},
    "app.tasks.clinical_trials_tasks.*": {"queue": "clinical"},
    "app.tasks.safety_tasks.*": {"queue": "safety"},
    "app.tasks.repurposing_tasks.*": {"queue": "repurposing"},
}


# Signal handlers for task lifecycle
@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Handle task start."""
    print(f"Task {task.name} [{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Handle task completion."""
    print(f"Task {task.name} [{task_id}] completed")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Handle task failure."""
    print(f"Task [{task_id}] failed with exception: {exception}")


if __name__ == "__main__":
    celery_app.start()

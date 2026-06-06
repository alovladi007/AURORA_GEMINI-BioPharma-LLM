"""
Shared Celery task infrastructure.

Provides a `TrackedTask` base class that keeps the corresponding `Job` DB row in
sync with the Celery task lifecycle, plus a `update_progress` helper for
long-running tasks to report incremental progress.

NOTE: the Job row is matched on `Job.task_id` (the Celery task id), which is the
actual column on the model.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from celery import Task

from app.core.database import SessionLocal
from app.models.job import Job, JobStatus

logger = logging.getLogger(__name__)


def _update_job(task_id: str, **fields: Any) -> None:
    """Apply field updates to the Job matched by Celery task id (best-effort)."""
    if not task_id:
        return
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.task_id == task_id).first()
        if job is None:
            return
        for key, value in fields.items():
            setattr(job, key, value)
        db.commit()
    except Exception:  # pragma: no cover - defensive; never crash the worker on bookkeeping
        db.rollback()
        logger.exception("Failed to update job for task %s", task_id)
    finally:
        db.close()


def update_progress(task_id: str, percent: int, message: Optional[str] = None) -> None:
    """Report incremental progress (0–100) and append a log line."""
    fields: dict[str, Any] = {"progress": max(0, min(100, int(percent)))}
    if message:
        fields["logs"] = message
    _update_job(task_id, **fields)


class TrackedTask(Task):
    """Celery Task base that mirrors lifecycle into the Job table."""

    def before_start(self, task_id: str, args: Any, kwargs: Any) -> None:  # noqa: D401
        _update_job(
            task_id,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
            progress=0,
        )

    def on_success(self, retval: Any, task_id: str, args: Any, kwargs: Any) -> None:
        # `result` is a JSON column — retval must be JSON-serializable.
        fields: dict[str, Any] = {
            "status": JobStatus.COMPLETED,
            "progress": 100,
            "completed_at": datetime.utcnow(),
        }
        if isinstance(retval, (dict, list)):
            fields["result"] = retval
        _update_job(task_id, **fields)

    def on_failure(self, exc: Any, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        _update_job(
            task_id,
            status=JobStatus.FAILED,
            error=str(exc),
            completed_at=datetime.utcnow(),
        )

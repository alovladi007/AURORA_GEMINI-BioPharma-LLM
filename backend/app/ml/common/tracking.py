"""
Optional MLflow experiment tracking.

All functions are best-effort: if MLflow isn't installed or the tracking server
is unreachable, tracking is silently skipped so it can never break training.
Enable by setting MLFLOW_TRACKING_URI (e.g. http://mlflow:5000).
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


@contextmanager
def mlflow_run(run_name: str, tags: Optional[Dict[str, Any]] = None) -> Iterator[Any]:
    """
    Context manager yielding an MLflow run handle, or None if tracking is disabled.

    Usage:
        with mlflow_run("sar-CHEMBL203") as run:
            log_params({...}); log_metrics({...})
    """
    if not settings.MLFLOW_TRACKING_URI:
        yield None
        return

    try:
        import mlflow  # type: ignore

        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(settings.MLFLOW_EXPERIMENT)
        with mlflow.start_run(run_name=run_name) as run:
            if tags:
                mlflow.set_tags(tags)
            yield run
    except Exception:  # pragma: no cover - tracking must never break training
        logger.warning("MLflow tracking unavailable; continuing without it", exc_info=True)
        yield None


def log_params(params: Dict[str, Any]) -> None:
    if not settings.MLFLOW_TRACKING_URI:
        return
    try:
        import mlflow  # type: ignore

        mlflow.log_params(params)
    except Exception:  # pragma: no cover
        logger.debug("MLflow log_params skipped", exc_info=True)


def log_metrics(metrics: Dict[str, float]) -> None:
    if not settings.MLFLOW_TRACKING_URI:
        return
    try:
        import mlflow  # type: ignore

        numeric = {k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))}
        if numeric:
            mlflow.log_metrics(numeric)
    except Exception:  # pragma: no cover
        logger.debug("MLflow log_metrics skipped", exc_info=True)


def log_artifact(path: str) -> None:
    if not settings.MLFLOW_TRACKING_URI:
        return
    try:
        import mlflow  # type: ignore

        mlflow.log_artifact(path)
    except Exception:  # pragma: no cover
        logger.debug("MLflow log_artifact skipped", exc_info=True)

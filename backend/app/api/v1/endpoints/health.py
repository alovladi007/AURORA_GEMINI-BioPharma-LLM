"""
Health check endpoints.

Provides system health status, including database and Redis connectivity.
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis
import logging

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Checks:
    - API service status
    - Database connectivity
    - Redis connectivity
    - Module availability

    Returns:
        Health status information including service statuses and timestamps.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
        "services": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    # Check Redis
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            socket_connect_timeout=5
        )
        r.ping()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["status"] = "degraded"  # Not critical for API operation
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }

    # Check module availability
    health_status["modules"] = {
        "drug_design": settings.ENABLE_DRUG_DESIGN,
        "clinical_trials": settings.ENABLE_CLINICAL_TRIALS,
        "repurposing": settings.ENABLE_REPURPOSING,
        "safety": settings.ENABLE_SAFETY,
    }

    # Return appropriate status code
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status


@router.get("/health/live", response_model=Dict[str, str])
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes-style liveness probe.

    Simple endpoint that returns OK if the application is running.
    Does not check external dependencies.

    Returns:
        Simple status indicating the API is alive.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/ready", response_model=Dict[str, Any])
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes-style readiness probe.

    Checks if the application is ready to serve traffic.
    Verifies critical dependencies (database).

    Returns:
        Readiness status with dependency checks.

    Raises:
        HTTPException: If critical dependencies are not available.
    """
    readiness_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database (critical)
    try:
        db.execute(text("SELECT 1"))
        readiness_status["checks"]["database"] = "ready"
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        readiness_status["status"] = "not_ready"
        readiness_status["checks"]["database"] = f"not_ready: {str(e)}"
        raise HTTPException(status_code=503, detail=readiness_status)

    return readiness_status


@router.get("/health/metrics", response_model=Dict[str, Any])
async def health_metrics() -> Dict[str, Any]:
    """
    Basic metrics endpoint.

    Returns system-level metrics and configuration.
    For production, integrate with Prometheus or similar.

    Returns:
        System metrics and configuration details.
    """
    import psutil
    import sys

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "python_version": sys.version,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        },
        "application": {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "modules_enabled": {
                "drug_design": settings.ENABLE_DRUG_DESIGN,
                "clinical_trials": settings.ENABLE_CLINICAL_TRIALS,
                "repurposing": settings.ENABLE_REPURPOSING,
                "safety": settings.ENABLE_SAFETY,
            }
        }
    }

    return metrics

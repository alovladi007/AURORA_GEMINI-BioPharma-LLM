"""
Pharma AI Platform - Main FastAPI Application
==============================================

Entry point for the backend API server.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.endpoints import health, projects, drug_design, safety, datasets, models, experiments, jobs, clinical_trials

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database tables (dev only - use Alembic in prod)
    if settings.INIT_DB and settings.ENVIRONMENT == "development":
        logger.info("Initializing database...")
        try:
            init_db()
            logger.info("✓ Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    logger.info(f"✓ {settings.PROJECT_NAME} started successfully")
    logger.info(f"API docs available at: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    **Production-ready AI platform for pharmaceutical research and drug development**

    ## Core Modules

    * **🧬 AI Drug Design** - De novo molecular generation, SAR prediction, lead optimization
    * **🏥 Clinical Trial Optimization** - Patient recruitment, trial design, safety monitoring
    * **♻️ Drug Repurposing** - Knowledge-graph mining, network prediction, RWE analysis
    * **⚠️ Safety & Toxicity** - ADMET prediction, toxicity modeling, DDI screening

    ## Features

    * RESTful API with auto-generated documentation
    * Asynchronous task processing with Celery
    * Role-based access control
    * Model registry and experiment tracking
    * Comprehensive ML pipelines for pharma research

    ## Getting Started

    1. Authenticate using `/api/v1/auth/login`
    2. Create a project using `/api/v1/projects`
    3. Upload datasets and run predictions
    4. Explore results through visualization endpoints

    ---
    **Note:** This platform is for research use only. All predictions must be validated
    through appropriate experimental and regulatory processes.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# ============================================
# Middleware Configuration
# ============================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Global Exception Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# ============================================
# API Routes
# ============================================

# Include health check endpoint
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Health"]
)

# Include projects endpoint
app.include_router(
    projects.router,
    prefix=f"{settings.API_V1_PREFIX}/projects",
    tags=["Projects"]
)

# Include drug design endpoint
app.include_router(
    drug_design.router,
    prefix=f"{settings.API_V1_PREFIX}/drug-design",
    tags=["Drug Design"]
)

# Include safety & toxicity endpoint
app.include_router(
    safety.router,
    prefix=f"{settings.API_V1_PREFIX}/safety",
    tags=["Safety & Toxicity"]
)

# Include datasets endpoint
app.include_router(
    datasets.router,
    prefix=f"{settings.API_V1_PREFIX}/datasets",
    tags=["Datasets"]
)

# Include models endpoint
app.include_router(
    models.router,
    prefix=f"{settings.API_V1_PREFIX}/models",
    tags=["Models"]
)

# Include experiments endpoint
app.include_router(
    experiments.router,
    prefix=f"{settings.API_V1_PREFIX}/experiments",
    tags=["Experiments"]
)

# Include jobs endpoint
app.include_router(
    jobs.router,
    prefix=f"{settings.API_V1_PREFIX}/jobs",
    tags=["Jobs"]
)

# Include clinical trials endpoint
app.include_router(
    clinical_trials.router,
    prefix=f"{settings.API_V1_PREFIX}/clinical-trials",
    tags=["Clinical Trials"]
)


# ============================================
# Root Endpoint
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.

    Returns:
        Basic API information and links to documentation.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "modules": {
            "drug_design": settings.ENABLE_DRUG_DESIGN,
            "clinical_trials": settings.ENABLE_CLINICAL_TRIALS,
            "repurposing": settings.ENABLE_REPURPOSING,
            "safety": settings.ENABLE_SAFETY,
        },
        "message": "Welcome to Pharma AI Platform API. Visit /docs for interactive documentation."
    }


# ============================================
# Development Helper Routes
# ============================================

if settings.DEBUG:
    @app.get("/debug/config", tags=["Debug"], include_in_schema=False)
    async def debug_config():
        """Debug endpoint to view configuration (dev only)."""
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database_configured": bool(settings.DATABASE_URL),
            "redis_configured": bool(settings.REDIS_HOST),
            "modules": {
                "drug_design": settings.ENABLE_DRUG_DESIGN,
                "clinical_trials": settings.ENABLE_CLINICAL_TRIALS,
                "repurposing": settings.ENABLE_REPURPOSING,
                "safety": settings.ENABLE_SAFETY,
            }
        }


# ============================================
# Application Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )

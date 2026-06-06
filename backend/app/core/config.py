"""
Configuration management for Pharma AI Platform.

Uses Pydantic Settings for type-safe configuration from environment variables.
"""

from typing import List, Optional
from pydantic import field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    See .env.example for all available configuration options.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    # ============================================
    # General
    # ============================================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ============================================
    # API
    # ============================================
    PROJECT_NAME: str = "Pharma AI Platform"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    # ============================================
    # Database
    # ============================================
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "pharma_user"
    POSTGRES_PASSWORD: str = "pharma_password_change_in_production"
    POSTGRES_DB: str = "pharma_db"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """Construct database URL if not provided."""
        if isinstance(v, str) and v:
            return v

        values = info.data
        return (
            f"postgresql://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_SERVER')}:"
            f"{values.get('POSTGRES_PORT')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    # ============================================
    # Redis
    # ============================================
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: Optional[str], info) -> str:
        """Construct Celery broker URL if not provided."""
        if isinstance(v, str) and v:
            return v

        values = info.data
        password = f":{values.get('REDIS_PASSWORD')}@" if values.get('REDIS_PASSWORD') else ""
        return f"redis://{password}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/0"

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: Optional[str], info) -> str:
        """Construct Celery result backend URL if not provided."""
        if isinstance(v, str) and v:
            return v

        values = info.data
        password = f":{values.get('REDIS_PASSWORD')}@" if values.get('REDIS_PASSWORD') else ""
        return f"redis://{password}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/0"

    # ============================================
    # Security
    # ============================================
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 8

    # ============================================
    # Machine Learning
    # ============================================
    MODEL_ARTIFACTS_PATH: str = "/app/ml/models/artifacts"
    DATASET_PATH: str = "/app/ml/data"

    DEFAULT_BATCH_SIZE: int = 32
    DEFAULT_NUM_EPOCHS: int = 100
    EARLY_STOPPING_PATIENCE: int = 10

    TORCH_DEVICE: str = "cpu"  # Set to "cuda" if GPU available

    # ============================================
    # Storage
    # ============================================
    STORAGE_BACKEND: str = "local"  # Options: local, s3
    STORAGE_LOCAL_PATH: str = "/app/storage"

    # S3 (if STORAGE_BACKEND=s3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # ============================================
    # Graph Database (Optional)
    # ============================================
    ENABLE_GRAPH_DB: bool = False
    NEO4J_URI: Optional[str] = None
    NEO4J_USER: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None

    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_DRUG_DESIGN: bool = True
    ENABLE_CLINICAL_TRIALS: bool = True
    ENABLE_REPURPOSING: bool = True
    ENABLE_SAFETY: bool = True

    # ============================================
    # Rate Limiting
    # ============================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # ============================================
    # Monitoring
    # ============================================
    SENTRY_DSN: Optional[str] = None
    LOG_FORMAT: str = "json"  # Options: json, text

    # MLflow experiment tracking (optional; skipped if unset/unreachable)
    MLFLOW_TRACKING_URI: Optional[str] = None
    MLFLOW_EXPERIMENT: str = "biopharma-llm"

    # ============================================
    # External APIs
    # ============================================
    PUBCHEM_API_URL: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    CHEMBL_API_URL: str = "https://www.ebi.ac.uk/chembl/api/data"
    CLINICALTRIALS_API_URL: str = "https://clinicaltrials.gov/api/v2"

    # ============================================
    # Development
    # ============================================
    RELOAD: bool = True
    INIT_DB: bool = True
    CREATE_SAMPLE_DATA: bool = True


# Create global settings instance
settings = Settings()


# Helper functions
def get_settings() -> Settings:
    """Get application settings instance."""
    return settings


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.ENVIRONMENT == "production"

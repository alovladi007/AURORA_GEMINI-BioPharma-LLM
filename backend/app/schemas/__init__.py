"""
Pydantic schemas for Pharma AI Platform.

Request/response schemas for API validation and serialization.
"""

# User schemas
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserWithProjects,
    PasswordChange,
    Token,
    TokenPayload,
)

# Project schemas
from app.schemas.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithCounts,
    ProjectSummary,
)

# Drug Design schemas
from app.schemas.drug_design import (
    MoleculeGenerationRequest,
    MoleculeGenerationResponse,
    GeneratedMolecule,
    SARPredictionRequest,
    SARPredictionResponse,
    SARPrediction,
    LeadOptimizationRequest,
    LeadOptimizationResponse,
    OptimizedMolecule,
)

# Dataset schemas
from app.schemas.dataset import (
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    DatasetSummary,
    DatasetWithStats,
)

# MLModel schemas
from app.schemas.model import (
    MLModel,
    MLModelCreate,
    MLModelUpdate,
    MLModelSummary,
    MLModelWithMetrics,
)

# Experiment schemas
from app.schemas.experiment import (
    Experiment,
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentSummary,
    ExperimentWithDuration,
)

# Job schemas
from app.schemas.job import (
    Job,
    JobCreate,
    JobUpdate,
    JobSummary,
    JobWithDuration,
)

# Safety schemas
from app.schemas.safety import (
    ADMETPredictionRequest,
    ADMETPredictionResponse,
    ADMETResult,
    ToxicityPredictionRequest,
    ToxicityPredictionResponse,
    ToxicityResult,
    ToxicityEndpoint,
    DDIScreeningRequest,
    DDIScreeningResponse,
    DDIInteraction,
    ToxicityLevel,
    ADMETProperty,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserWithProjects",
    "PasswordChange",
    "Token",
    "TokenPayload",
    # Project
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectWithCounts",
    "ProjectSummary",
    # Drug Design
    "MoleculeGenerationRequest",
    "MoleculeGenerationResponse",
    "GeneratedMolecule",
    "SARPredictionRequest",
    "SARPredictionResponse",
    "SARPrediction",
    "LeadOptimizationRequest",
    "LeadOptimizationResponse",
    "OptimizedMolecule",
    # Safety
    "ADMETPredictionRequest",
    "ADMETPredictionResponse",
    "ADMETResult",
    "ToxicityPredictionRequest",
    "ToxicityPredictionResponse",
    "ToxicityResult",
    "ToxicityEndpoint",
    "DDIScreeningRequest",
    "DDIScreeningResponse",
    "DDIInteraction",
    "ToxicityLevel",
    "ADMETProperty",
]

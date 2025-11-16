"""
Pydantic schemas for AI Drug Design module.

Request/response schemas for molecular generation, SAR prediction, and optimization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============================================
# De Novo Generation Schemas
# ============================================

class MoleculeGenerationRequest(BaseModel):
    """Request schema for de novo molecular generation."""
    num_molecules: int = Field(default=10, ge=1, le=1000, description="Number of molecules to generate")
    target_property: Optional[str] = Field(None, description="Target property to optimize (e.g., 'activity', 'logP')")
    target_value: Optional[float] = Field(None, description="Target value for the property")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Molecular constraints (MW, HBD, HBA, etc.)")
    model_version: Optional[str] = Field("latest", description="Model version to use")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "num_molecules": 20,
                "target_property": "activity",
                "target_value": 7.0,
                "constraints": {
                    "MW": [200, 500],
                    "LogP": [-1, 5],
                    "HBD": [0, 5]
                },
                "model_version": "latest"
            }
        }
    )


class GeneratedMolecule(BaseModel):
    """Schema for a single generated molecule."""
    smiles: str
    predicted_activity: Optional[float] = None
    predicted_properties: Optional[Dict[str, float]] = None
    similarity_score: Optional[float] = None
    validity: bool = True

    model_config = ConfigDict(from_attributes=True)


class MoleculeGenerationResponse(BaseModel):
    """Response schema for molecular generation."""
    molecules: List[GeneratedMolecule]
    generation_time: float
    model_version: str
    total_generated: int
    valid_count: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "molecules": [
                    {
                        "smiles": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
                        "predicted_activity": 7.2,
                        "predicted_properties": {"MW": 206.28, "LogP": 3.5, "HBD": 1},
                        "validity": True
                    }
                ],
                "generation_time": 2.5,
                "model_version": "v1.0",
                "total_generated": 20,
                "valid_count": 18
            }
        }
    )


# ============================================
# SAR Prediction Schemas
# ============================================

class SARPredictionRequest(BaseModel):
    """Request schema for SAR prediction."""
    smiles: List[str] = Field(..., min_length=1, description="List of SMILES strings")
    target: Optional[str] = Field(None, description="Target protein/receptor")
    model_version: Optional[str] = Field("latest", description="Model version to use")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "smiles": ["CCO", "CC(C)O", "CCCO"],
                "target": "EGFR",
                "model_version": "latest"
            }
        }
    )


class SARPrediction(BaseModel):
    """Schema for SAR prediction result."""
    smiles: str
    predicted_activity: float
    confidence: Optional[float] = None
    important_features: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class SARPredictionResponse(BaseModel):
    """Response schema for SAR predictions."""
    predictions: List[SARPrediction]
    model_version: str
    target: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predictions": [
                    {
                        "smiles": "CCO",
                        "predicted_activity": 5.2,
                        "confidence": 0.85,
                        "important_features": ["aromatic_rings", "hydrogen_bond_donors"]
                    }
                ],
                "model_version": "v1.0",
                "target": "EGFR"
            }
        }
    )


# ============================================
# Lead Optimization Schemas
# ============================================

class LeadOptimizationRequest(BaseModel):
    """Request schema for lead optimization."""
    lead_smiles: str = Field(..., description="SMILES of lead compound")
    objectives: Dict[str, float] = Field(..., description="Optimization objectives (property: target_value)")
    num_analogs: int = Field(default=50, ge=1, le=500, description="Number of analogs to generate")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum Tanimoto similarity")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lead_smiles": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
                "objectives": {
                    "activity": 8.0,
                    "LogP": 2.5,
                    "solubility": -3.0
                },
                "num_analogs": 100,
                "similarity_threshold": 0.7
            }
        }
    )


class OptimizedMolecule(BaseModel):
    """Schema for optimized molecule analog."""
    smiles: str
    predicted_properties: Dict[str, float]
    similarity_to_lead: float
    optimization_score: float
    pareto_rank: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class LeadOptimizationResponse(BaseModel):
    """Response schema for lead optimization."""
    lead_smiles: str
    optimized_molecules: List[OptimizedMolecule]
    objectives: Dict[str, float]
    optimization_time: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lead_smiles": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
                "optimized_molecules": [
                    {
                        "smiles": "CC(C)Cc1ccc(C(C)C(=O)N)cc1",
                        "predicted_properties": {"activity": 7.8, "LogP": 2.3, "solubility": -3.2},
                        "similarity_to_lead": 0.85,
                        "optimization_score": 0.92,
                        "pareto_rank": 1
                    }
                ],
                "objectives": {"activity": 8.0, "LogP": 2.5, "solubility": -3.0},
                "optimization_time": 15.3
            }
        }
    )

"""
Pydantic schemas for Safety & Toxicity module.

Request/response schemas for ADMET prediction, toxicity assessment, and DDI screening.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# ============================================
# Enums
# ============================================

class ToxicityLevel(str, Enum):
    """Toxicity risk levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ADMETProperty(str, Enum):
    """ADMET property types."""
    ABSORPTION = "absorption"
    DISTRIBUTION = "distribution"
    METABOLISM = "metabolism"
    EXCRETION = "excretion"
    TOXICITY = "toxicity"


# ============================================
# ADMET Prediction Schemas
# ============================================

class ADMETPredictionRequest(BaseModel):
    """Request schema for ADMET prediction."""
    smiles: List[str] = Field(..., min_length=1, description="List of SMILES strings")
    properties: Optional[List[ADMETProperty]] = Field(None, description="Specific properties to predict")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "smiles": ["CCO", "CC(C)O"],
                "properties": ["absorption", "distribution", "toxicity"]
            }
        }
    )


class ADMETResult(BaseModel):
    """ADMET prediction result for a single molecule."""
    smiles: str
    absorption: Optional[Dict[str, float]] = Field(None, description="Absorption properties (Caco2, HIA, etc.)")
    distribution: Optional[Dict[str, float]] = Field(None, description="Distribution properties (BBB, PPB, VDss)")
    metabolism: Optional[Dict[str, float]] = Field(None, description="Metabolism properties (CYP interactions)")
    excretion: Optional[Dict[str, float]] = Field(None, description="Excretion properties (clearance, half-life)")
    toxicity: Optional[Dict[str, float]] = Field(None, description="Toxicity endpoints")
    overall_score: Optional[float] = Field(None, description="Overall ADMET score (0-1)")

    model_config = ConfigDict(from_attributes=True)


class ADMETPredictionResponse(BaseModel):
    """Response schema for ADMET predictions."""
    results: List[ADMETResult]
    model_version: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "smiles": "CCO",
                        "absorption": {"Caco2": 0.8, "HIA": 0.95},
                        "distribution": {"BBB": 0.3, "PPB": 0.65},
                        "metabolism": {"CYP3A4_substrate": 0.2},
                        "excretion": {"half_life": 4.5},
                        "toxicity": {"hERG": 0.1, "hepatotoxicity": 0.15},
                        "overall_score": 0.75
                    }
                ],
                "model_version": "v1.0"
            }
        }
    )


# ============================================
# Toxicity Prediction Schemas
# ============================================

class ToxicityPredictionRequest(BaseModel):
    """Request schema for toxicity prediction."""
    smiles: List[str] = Field(..., min_length=1, description="List of SMILES strings")
    endpoints: Optional[List[str]] = Field(None, description="Specific toxicity endpoints")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "smiles": ["CCO", "CC(C)O"],
                "endpoints": ["hepatotoxicity", "cardiotoxicity", "nephrotoxicity"]
            }
        }
    )


class ToxicityEndpoint(BaseModel):
    """Toxicity prediction for a specific endpoint."""
    endpoint: str
    probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: ToxicityLevel
    confidence: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ToxicityResult(BaseModel):
    """Toxicity prediction result for a single molecule."""
    smiles: str
    endpoints: List[ToxicityEndpoint]
    overall_risk: ToxicityLevel
    alerts: Optional[List[str]] = Field(None, description="Structural alerts")

    model_config = ConfigDict(from_attributes=True)


class ToxicityPredictionResponse(BaseModel):
    """Response schema for toxicity predictions."""
    results: List[ToxicityResult]
    model_version: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "smiles": "CCO",
                        "endpoints": [
                            {"endpoint": "hepatotoxicity", "probability": 0.15, "risk_level": "low", "confidence": 0.88},
                            {"endpoint": "cardiotoxicity", "probability": 0.65, "risk_level": "moderate", "confidence": 0.82}
                        ],
                        "overall_risk": "moderate",
                        "alerts": ["Contains alcohol group"]
                    }
                ],
                "model_version": "v1.0"
            }
        }
    )


# ============================================
# DDI Screening Schemas
# ============================================

class DDIScreeningRequest(BaseModel):
    """Request schema for drug-drug interaction screening."""
    drug_pairs: List[tuple[str, str]] = Field(..., description="List of (drug1_smiles, drug2_smiles) tuples")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "drug_pairs": [["CCO", "CC(C)O"], ["CCCO", "CCCCO"]]
            }
        }
    )


class DDIInteraction(BaseModel):
    """DDI screening result for a drug pair."""
    drug1_smiles: str
    drug2_smiles: str
    interaction_probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: ToxicityLevel
    mechanism: Optional[str] = None
    recommendation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DDIScreeningResponse(BaseModel):
    """Response schema for DDI screening."""
    interactions: List[DDIInteraction]
    model_version: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "interactions": [
                    {
                        "drug1_smiles": "CCO",
                        "drug2_smiles": "CC(C)O",
                        "interaction_probability": 0.35,
                        "risk_level": "low",
                        "mechanism": "CYP3A4 competition",
                        "recommendation": "Monitor patient closely"
                    }
                ],
                "model_version": "v1.0"
            }
        }
    )

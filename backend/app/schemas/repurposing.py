"""
Drug Repurposing schemas.

Request/response schemas for drug repurposing endpoints.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# Knowledge Graph Mining
class KnowledgeGraphRequest(BaseModel):
    """Request for knowledge graph mining."""
    drug_name: str = Field(..., description="Drug name or identifier")
    max_paths: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of paths to return")
    path_length: Optional[int] = Field(3, ge=2, le=5, description="Maximum path length")


class PathNode(BaseModel):
    """Node in a knowledge graph path."""
    node_id: str
    node_type: str = Field(..., description="Node type (drug/disease/target/pathway)")
    name: str
    properties: Optional[Dict[str, Any]] = None


class KnowledgePath(BaseModel):
    """Path in knowledge graph."""
    path_id: str
    nodes: List[PathNode]
    confidence_score: float = Field(..., ge=0, le=1)
    supporting_evidence: List[str]


class IndicationCandidate(BaseModel):
    """Candidate indication for repurposing."""
    disease_name: str
    disease_id: str
    confidence_score: float = Field(..., ge=0, le=1)
    shared_targets: List[str]
    mechanism_similarity: float = Field(..., ge=0, le=1)
    clinical_evidence: Optional[str] = None


class KnowledgeGraphResponse(BaseModel):
    """Response for knowledge graph mining."""
    drug_name: str
    total_paths_found: int
    paths: List[KnowledgePath]
    candidate_indications: List[IndicationCandidate]
    network_statistics: Dict[str, Any]


# Mechanism Prediction
class MechanismPredictionRequest(BaseModel):
    """Request for mechanism of action prediction."""
    drug_name: str = Field(..., description="Drug name")
    disease_name: str = Field(..., description="Target disease")
    include_pathways: Optional[bool] = Field(True, description="Include pathway analysis")


class TargetPrediction(BaseModel):
    """Predicted target for drug."""
    target_name: str
    target_id: str
    prediction_confidence: float = Field(..., ge=0, le=1)
    interaction_type: str = Field(..., description="agonist/antagonist/inhibitor/activator")
    supporting_evidence: List[str]


class PathwayEnrichment(BaseModel):
    """Enriched pathway."""
    pathway_name: str
    pathway_id: str
    p_value: float
    enrichment_score: float
    genes_involved: List[str]


class MechanismPredictionResponse(BaseModel):
    """Response for mechanism prediction."""
    drug_name: str
    disease_name: str
    predicted_targets: List[TargetPrediction]
    enriched_pathways: List[PathwayEnrichment]
    mechanism_summary: str
    confidence_score: float = Field(..., ge=0, le=1)


# Drug Combination Discovery
class CombinationDiscoveryRequest(BaseModel):
    """Request for drug combination discovery."""
    anchor_drug: str = Field(..., description="Primary drug name")
    indication: str = Field(..., description="Disease indication")
    max_combinations: Optional[int] = Field(10, ge=1, le=50, description="Max combinations to return")
    synergy_threshold: Optional[float] = Field(0.5, ge=0, le=1, description="Minimum synergy score")


class DrugCombination(BaseModel):
    """Drug combination candidate."""
    partner_drug: str
    partner_drug_id: str
    synergy_score: float = Field(..., ge=0, le=1, description="Predicted synergy score")
    mechanism_complementarity: str
    shared_targets: List[str]
    unique_targets: List[str]
    safety_concerns: Optional[List[str]] = None
    clinical_evidence: Optional[str] = None


class CombinationDiscoveryResponse(BaseModel):
    """Response for combination discovery."""
    anchor_drug: str
    indication: str
    total_combinations_evaluated: int
    recommended_combinations: List[DrugCombination]
    analysis_summary: str

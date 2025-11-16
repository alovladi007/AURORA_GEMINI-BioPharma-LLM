"""
Drug Repurposing API endpoints.

Provides knowledge graph mining, mechanism prediction, and combination discovery.
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.schemas.repurposing import (
    KnowledgeGraphRequest,
    KnowledgeGraphResponse,
    MechanismPredictionRequest,
    MechanismPredictionResponse,
    CombinationDiscoveryRequest,
    CombinationDiscoveryResponse,
)
from app.ml.repurposing.inference import DrugRepurposingEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize global engine
_repurposing_engine = None


def get_repurposing_engine() -> DrugRepurposingEngine:
    """Get or create drug repurposing engine."""
    global _repurposing_engine

    if _repurposing_engine is None:
        logger.info("Initializing Drug Repurposing engine...")
        _repurposing_engine = DrugRepurposingEngine()

    return _repurposing_engine


@router.post("/knowledge-graph", response_model=KnowledgeGraphResponse)
def mine_knowledge_graph(request: KnowledgeGraphRequest):
    """
    Mine knowledge graph for drug repurposing opportunities.

    **Request Parameters:**
    - **drug_name**: Name of the drug to analyze
    - **max_paths**: Maximum number of paths to return (default: 10)
    - **path_length**: Maximum path length (default: 3)

    **Returns:**
    - Knowledge graph paths connecting drug to potential indications
    - Candidate diseases for repurposing
    - Network statistics and confidence scores
    - Supporting evidence for each path

    **Example:**
    ```json
    {
        "drug_name": "Metformin",
        "max_paths": 15,
        "path_length": 4
    }
    ```
    """
    try:
        engine = get_repurposing_engine()

        result = engine.mine_knowledge_graph(
            drug_name=request.drug_name,
            max_paths=request.max_paths,
            path_length=request.path_length,
        )

        return KnowledgeGraphResponse(**result)

    except Exception as e:
        logger.error(f"Error mining knowledge graph: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mine knowledge graph: {str(e)}"
        )


@router.post("/mechanism", response_model=MechanismPredictionResponse)
def predict_mechanism(request: MechanismPredictionRequest):
    """
    Predict mechanism of action for drug-disease pair.

    **Request Parameters:**
    - **drug_name**: Name of the drug
    - **disease_name**: Target disease or indication
    - **include_pathways**: Include pathway enrichment analysis (default: true)

    **Returns:**
    - Predicted molecular targets and interaction types
    - Enriched biological pathways
    - Mechanism summary
    - Confidence scores and supporting evidence

    **Example:**
    ```json
    {
        "drug_name": "Aspirin",
        "disease_name": "Alzheimer's Disease",
        "include_pathways": true
    }
    ```
    """
    try:
        engine = get_repurposing_engine()

        result = engine.predict_mechanism(
            drug_name=request.drug_name,
            disease_name=request.disease_name,
            include_pathways=request.include_pathways,
        )

        return MechanismPredictionResponse(**result)

    except Exception as e:
        logger.error(f"Error predicting mechanism: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict mechanism: {str(e)}"
        )


@router.post("/combinations", response_model=CombinationDiscoveryResponse)
def discover_combinations(request: CombinationDiscoveryRequest):
    """
    Discover synergistic drug combinations.

    **Request Parameters:**
    - **anchor_drug**: Primary drug for combination therapy
    - **indication**: Disease indication
    - **max_combinations**: Maximum combinations to return (default: 10)
    - **synergy_threshold**: Minimum synergy score (default: 0.5)

    **Returns:**
    - Recommended drug combinations ranked by synergy score
    - Mechanism complementarity analysis
    - Shared and unique molecular targets
    - Safety concerns and clinical evidence

    **Example:**
    ```json
    {
        "anchor_drug": "Pembrolizumab",
        "indication": "Non-Small Cell Lung Cancer",
        "max_combinations": 15,
        "synergy_threshold": 0.6
    }
    ```
    """
    try:
        engine = get_repurposing_engine()

        result = engine.discover_combinations(
            anchor_drug=request.anchor_drug,
            indication=request.indication,
            max_combinations=request.max_combinations,
            synergy_threshold=request.synergy_threshold,
        )

        return CombinationDiscoveryResponse(**result)

    except Exception as e:
        logger.error(f"Error discovering combinations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover combinations: {str(e)}"
        )

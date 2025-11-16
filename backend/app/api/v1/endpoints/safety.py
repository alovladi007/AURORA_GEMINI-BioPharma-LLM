"""
Safety & Toxicity API endpoints.

Provides ADMET prediction, toxicity assessment, and DDI screening.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
import logging

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
)
from app.ml.safety.inference import SafetyInferenceEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize global inference engine (lazy loading)
_safety_engine = None


def get_safety_engine() -> SafetyInferenceEngine:
    """Get or create safety inference engine."""
    global _safety_engine

    if _safety_engine is None:
        logger.info("Initializing safety inference engine...")
        _safety_engine = SafetyInferenceEngine()

    return _safety_engine


@router.post("/admet", response_model=ADMETPredictionResponse)
def predict_admet(request: ADMETPredictionRequest):
    """
    Predict ADMET properties for molecules.

    **Request Parameters:**
    - **smiles**: List of SMILES strings (required)
    - **properties**: Specific ADMET properties to predict (optional, predicts all if not specified)

    **Returns:**
    - ADMET predictions for each molecule including:
      - Absorption (Caco2, HIA, bioavailability)
      - Distribution (BBB, PPB, VDss)
      - Metabolism (CYP substrates)
      - Excretion (half-life, clearance)
      - Toxicity (hERG, hepatotoxicity, AMES)
      - Overall ADMET score

    **Example:**
    ```json
    {
        "smiles": ["CCO", "CC(C)O"],
        "properties": ["absorption", "toxicity"]
    }
    ```
    """
    try:
        engine = get_safety_engine()

        # Predict ADMET
        predictions = engine.predict_admet(request.smiles)

        # Convert to response schema
        results = []
        for pred in predictions:
            if "error" in pred:
                logger.warning(f"ADMET prediction error for {pred['smiles']}: {pred['error']}")
                continue

            results.append(ADMETResult(
                smiles=pred["smiles"],
                absorption=pred.get("absorption"),
                distribution=pred.get("distribution"),
                metabolism=pred.get("metabolism"),
                excretion=pred.get("excretion"),
                toxicity=pred.get("toxicity"),
                overall_score=pred.get("overall_score")
            ))

        return ADMETPredictionResponse(
            results=results,
            model_version="rule-based-v1.0"
        )

    except Exception as e:
        logger.error(f"Error predicting ADMET: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict ADMET: {str(e)}"
        )


@router.post("/toxicity", response_model=ToxicityPredictionResponse)
def predict_toxicity(request: ToxicityPredictionRequest):
    """
    Predict toxicity endpoints for molecules.

    **Request Parameters:**
    - **smiles**: List of SMILES strings (required)
    - **endpoints**: Specific toxicity endpoints to predict (optional, predicts all if not specified)

    **Supported Endpoints:**
    - hepatotoxicity: Liver toxicity
    - cardiotoxicity: Heart toxicity (including hERG)
    - nephrotoxicity: Kidney toxicity
    - neurotoxicity: Nervous system toxicity
    - genotoxicity: DNA damage
    - carcinogenicity: Cancer-causing potential
    - skin_sensitization: Allergic skin reactions

    **Returns:**
    - Toxicity predictions for each endpoint with:
      - Probability score (0-1)
      - Risk level (low, moderate, high)
      - Confidence score
      - Structural alerts

    **Example:**
    ```json
    {
        "smiles": ["CCO", "CC(C)O"],
        "endpoints": ["hepatotoxicity", "cardiotoxicity"]
    }
    ```
    """
    try:
        engine = get_safety_engine()

        # Predict toxicity
        predictions = engine.predict_toxicity(request.smiles, request.endpoints)

        # Convert to response schema
        results = []
        for pred in predictions:
            if "error" in pred:
                logger.warning(f"Toxicity prediction error for {pred['smiles']}: {pred['error']}")
                continue

            # Convert endpoints to schema
            endpoints = [
                ToxicityEndpoint(
                    endpoint=ep["endpoint"],
                    probability=ep["probability"],
                    risk_level=ToxicityLevel(ep["risk_level"]),
                    confidence=ep.get("confidence")
                )
                for ep in pred["endpoints"]
            ]

            results.append(ToxicityResult(
                smiles=pred["smiles"],
                endpoints=endpoints,
                overall_risk=ToxicityLevel(pred["overall_risk"]),
                alerts=pred.get("alerts")
            ))

        return ToxicityPredictionResponse(
            results=results,
            model_version="rule-based-v1.0"
        )

    except Exception as e:
        logger.error(f"Error predicting toxicity: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict toxicity: {str(e)}"
        )


@router.post("/ddi", response_model=DDIScreeningResponse)
def screen_ddi(request: DDIScreeningRequest):
    """
    Screen for drug-drug interactions.

    **Request Parameters:**
    - **drug_pairs**: List of (drug1_smiles, drug2_smiles) tuples (required)

    **Returns:**
    - DDI predictions for each pair including:
      - Interaction probability (0-1)
      - Risk level (low, moderate, high)
      - Interaction mechanism
      - Clinical recommendation

    **Mechanisms Detected:**
    - CYP enzyme competition
    - P-glycoprotein (P-gp) interaction
    - Pharmacokinetic interactions

    **Example:**
    ```json
    {
        "drug_pairs": [
            ["CCO", "CC(C)O"],
            ["CCCO", "CCCCO"]
        ]
    }
    ```
    """
    try:
        engine = get_safety_engine()

        # Screen DDI
        predictions = engine.screen_ddi(request.drug_pairs)

        # Convert to response schema
        interactions = []
        for pred in predictions:
            if "error" in pred:
                logger.warning(f"DDI screening error: {pred['error']}")
                continue

            interactions.append(DDIInteraction(
                drug1_smiles=pred["drug1_smiles"],
                drug2_smiles=pred["drug2_smiles"],
                interaction_probability=pred["interaction_probability"],
                risk_level=ToxicityLevel(pred["risk_level"]),
                mechanism=pred.get("mechanism"),
                recommendation=pred.get("recommendation")
            ))

        return DDIScreeningResponse(
            interactions=interactions,
            model_version="rule-based-v1.0"
        )

    except Exception as e:
        logger.error(f"Error screening DDI: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to screen DDI: {str(e)}"
        )

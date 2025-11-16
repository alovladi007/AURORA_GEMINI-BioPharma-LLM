"""
Drug Design API endpoints.

Provides molecular generation, SAR prediction, and lead optimization.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
import logging
from pathlib import Path

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
from app.ml.drug_design.inference import (
    SAR

InferenceEngine,
    MolecularGenerator,
    create_demo_sar_model,
)
from app.ml.common.featurization import MolecularFeaturizer
from app.core.config import settings
import time

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize global inference engines (lazy loading)
_sar_engine = None
_molecular_generator = None


def get_sar_engine() -> SARInferenceEngine:
    """Get or create SAR inference engine."""
    global _sar_engine

    if _sar_engine is None:
        logger.info("Initializing SAR inference engine...")

        # Try to load model, or create demo model
        model_path = Path(settings.MODEL_ARTIFACTS_PATH) / "drug_design" / "sar_model.pkl"

        if model_path.exists():
            _sar_engine = SARInferenceEngine(model_path=str(model_path), model_type="random_forest")
        else:
            # Create and save demo model
            logger.warning("No trained SAR model found. Creating demo model...")
            model_path.parent.mkdir(parents=True, exist_ok=True)
            create_demo_sar_model(save_path=str(model_path))
            _sar_engine = SARInferenceEngine(model_path=str(model_path), model_type="random_forest")

    return _sar_engine


def get_molecular_generator() -> MolecularGenerator:
    """Get or create molecular generator."""
    global _molecular_generator

    if _molecular_generator is None:
        logger.info("Initializing molecular generator...")
        _molecular_generator = MolecularGenerator()

    return _molecular_generator


@router.post("/generate", response_model=MoleculeGenerationResponse)
def generate_molecules(request: MoleculeGenerationRequest):
    """
    Generate novel molecules using AI.

    **Request Parameters:**
    - **num_molecules**: Number of molecules to generate (1-1000)
    - **target_property**: Target property to optimize (optional)
    - **target_value**: Target value for the property (optional)
    - **constraints**: Molecular constraints (MW, LogP, etc.) (optional)
    - **model_version**: Model version to use (default: "latest")

    **Returns:**
    - List of generated molecules with predicted properties
    - Generation time and statistics

    **Note:**
    This is a baseline implementation using random generation.
    In production, use trained generative models (VAE, GAN, Transformers).

    **Example:**
    ```json
    {
        "num_molecules": 20,
        "target_property": "activity",
        "target_value": 7.0,
        "constraints": {"MW": [200, 500], "LogP": [-1, 5]}
    }
    ```
    """
    start_time = time.time()

    try:
        generator = get_molecular_generator()
        featurizer = MolecularFeaturizer()

        # Generate molecules
        generated_smiles = generator.generate_random_molecules(num_molecules=request.num_molecules)

        # Process each molecule
        molecules = []
        valid_count = 0

        for smiles in generated_smiles:
            # Check validity
            mol = featurizer.smiles_to_mol(smiles)
            is_valid = mol is not None

            if is_valid:
                valid_count += 1

                # Compute properties
                descriptors = featurizer.compute_descriptors(smiles)
                predicted_properties = {
                    "MW": descriptors["molecular_weight"],
                    "LogP": descriptors["logP"],
                    "HBD": descriptors["num_h_donors"],
                    "HBA": descriptors["num_h_acceptors"],
                    "TPSA": descriptors["tpsa"],
                } if descriptors else None

                # For demo, use QED as activity proxy
                predicted_activity = descriptors["qed"] * 10 if descriptors else None

                molecules.append(GeneratedMolecule(
                    smiles=smiles,
                    predicted_activity=predicted_activity,
                    predicted_properties=predicted_properties,
                    validity=True
                ))

        generation_time = time.time() - start_time

        return MoleculeGenerationResponse(
            molecules=molecules,
            generation_time=generation_time,
            model_version=request.model_version or "demo-v1.0",
            total_generated=len(generated_smiles),
            valid_count=valid_count
        )

    except Exception as e:
        logger.error(f"Error generating molecules: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate molecules: {str(e)}"
        )


@router.post("/predict-sar", response_model=SARPredictionResponse)
def predict_sar(request: SARPredictionRequest):
    """
    Predict structure-activity relationships for molecules.

    **Request Parameters:**
    - **smiles**: List of SMILES strings (required)
    - **target**: Target protein/receptor (optional, for context)
    - **model_version**: Model version to use (default: "latest")

    **Returns:**
    - Predicted activity scores for each molecule
    - Confidence scores
    - Important molecular features

    **Example:**
    ```json
    {
        "smiles": ["CCO", "CC(C)O", "CCCO"],
        "target": "EGFR",
        "model_version": "latest"
    }
    ```
    """
    try:
        engine = get_sar_engine()

        # Make predictions
        predictions_data = engine.predict_with_descriptors(request.smiles)

        # Convert to response schema
        predictions = []
        for pred in predictions_data:
            # Extract important features (top descriptors by value)
            important_features = []
            if "descriptors" in pred:
                desc = pred["descriptors"]
                # Get top 5 descriptors by absolute value
                sorted_desc = sorted(desc.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
                important_features = [f"{k}={v:.2f}" for k, v in sorted_desc]

            predictions.append(SARPrediction(
                smiles=pred["smiles"],
                predicted_activity=pred.get("predicted_activity", 0.0),
                confidence=pred.get("confidence"),
                important_features=important_features if important_features else None
            ))

        return SARPredictionResponse(
            predictions=predictions,
            model_version=request.model_version or "demo-v1.0",
            target=request.target
        )

    except Exception as e:
        logger.error(f"Error predicting SAR: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict SAR: {str(e)}"
        )


@router.post("/optimize", response_model=LeadOptimizationResponse)
def optimize_lead(request: LeadOptimizationRequest):
    """
    Optimize a lead compound for better properties.

    **Request Parameters:**
    - **lead_smiles**: SMILES of lead compound (required)
    - **objectives**: Optimization objectives with target values (required)
    - **num_analogs**: Number of analogs to generate (default: 50, max: 500)
    - **similarity_threshold**: Minimum Tanimoto similarity (default: 0.7)

    **Returns:**
    - List of optimized analogs ranked by optimization score
    - Predicted properties for each analog
    - Similarity to lead compound

    **Note:**
    This is a baseline implementation using similarity-based filtering.
    In production, use optimization algorithms (genetic algorithms, RL).

    **Example:**
    ```json
    {
        "lead_smiles": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "objectives": {
            "activity": 8.0,
            "LogP": 2.5,
            "solubility": -3.0
        },
        "num_analogs": 100,
        "similarity_threshold": 0.7
    }
    ```
    """
    start_time = time.time()

    try:
        generator = get_molecular_generator()
        featurizer = MolecularFeaturizer()
        sar_engine = get_sar_engine()

        # Validate lead SMILES
        lead_mol = featurizer.smiles_to_mol(request.lead_smiles)
        if lead_mol is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid lead SMILES: {request.lead_smiles}"
            )

        # Generate analogs
        analogs = generator.optimize_molecule(
            lead_smiles=request.lead_smiles,
            num_analogs=request.num_analogs,
            similarity_threshold=request.similarity_threshold
        )

        # Score each analog
        optimized_molecules = []

        for analog in analogs:
            smiles = analog["smiles"]

            # Get predicted properties
            descriptors = featurizer.compute_descriptors(smiles)
            if not descriptors:
                continue

            predicted_properties = {
                "activity": descriptors["qed"] * 10,  # Use QED as activity proxy
                "LogP": descriptors["logP"],
                "MW": descriptors["molecular_weight"],
                "TPSA": descriptors["tpsa"],
            }

            # Compute optimization score (distance from objectives)
            optimization_score = 0.0
            num_objectives = 0

            for obj_name, obj_value in request.objectives.items():
                if obj_name in predicted_properties:
                    # Normalized distance (closer to 1 is better)
                    distance = abs(predicted_properties[obj_name] - obj_value)
                    norm_score = max(0.0, 1.0 - distance / (abs(obj_value) + 1e-6))
                    optimization_score += norm_score
                    num_objectives += 1

            if num_objectives > 0:
                optimization_score /= num_objectives

            optimized_molecules.append(OptimizedMolecule(
                smiles=smiles,
                predicted_properties=predicted_properties,
                similarity_to_lead=analog["similarity_to_lead"],
                optimization_score=optimization_score
            ))

        # Sort by optimization score
        optimized_molecules = sorted(
            optimized_molecules,
            key=lambda x: x.optimization_score,
            reverse=True
        )

        optimization_time = time.time() - start_time

        return LeadOptimizationResponse(
            lead_smiles=request.lead_smiles,
            optimized_molecules=optimized_molecules,
            objectives=request.objectives,
            optimization_time=optimization_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing lead: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize lead: {str(e)}"
        )

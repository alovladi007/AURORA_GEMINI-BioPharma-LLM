"""
Celery tasks for the Drug Design module.

The flagship task is `train_sar_task`, which runs the **real** SAR training
pipeline (ChEMBL ingestion → scaffold split → RandomForest → model card) as a
tracked background Job, and registers the resulting model in the model registry.

Inference tasks wrap the existing engines for async execution of heavier batches.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.celery_app import celery_app
from app.tasks.base import TrackedTask, update_progress

logger = logging.getLogger(__name__)


@celery_app.task(base=TrackedTask, bind=True, name="drug_design.train_sar")
def train_sar_task(
    self,
    input_csv: Optional[str] = None,
    target: Optional[str] = None,
    model_name: str = "sar_random_forest",
    project_id: Optional[int] = None,
    max_records: Optional[int] = None,
    n_estimators: int = 300,
    max_depth: int = 20,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Train a real SAR model as a tracked job.

    Args:
        input_csv: curated CSV (smiles,label[,pchembl_value]); or
        target: ChEMBL target id to ingest if input_csv is absent.
        model_name: artifact base name.
        project_id: if provided, register the trained model under this project.

    Returns:
        Result dict from `train_sar` (metrics, artifact path, model card path).
    """
    from app.ml.drug_design.train import train_sar

    task_id = self.request.id

    def _progress(percent: int, message: str) -> None:
        update_progress(task_id, percent, message)

    result = train_sar(
        input_csv=input_csv,
        target=target,
        max_records=max_records,
        model_name=model_name,
        n_estimators=n_estimators,
        max_depth=max_depth,
        seed=seed,
        progress=_progress,
    )

    # Best-effort registration in the model registry (never fail the job on this).
    if project_id is not None:
        try:
            _register_model(result, project_id)
        except Exception:  # pragma: no cover - defensive
            logger.exception("Model registration failed for %s", model_name)

    return result


def _register_model(result: Dict[str, Any], project_id: int) -> None:
    """Create + mark READY an MLModel row for a finished training run."""
    from app.core.database import SessionLocal
    from app.models.model import ModelStatus, ModelType
    from app.schemas.model import MLModelCreate, MLModelUpdate
    from app.services.model_service import MLModelService

    db = SessionLocal()
    try:
        created = MLModelService.create_model(
            db,
            MLModelCreate(
                name=result["model_name"],
                description=f"SAR classifier trained on {result['data_source']}",
                model_type=ModelType.DRUG_DESIGN_SAR,
                version="1.0.0",
                framework="sklearn",
                hyperparameters=result.get("hyperparameters"),
                project_id=project_id,
            ),
        )
        # Fold artifact path into metrics (file_path isn't in the update schema).
        metrics = dict(result.get("test_metrics") or {})
        metrics["artifact_path"] = result.get("artifact_path")
        MLModelService.update_model(
            db,
            created.id,
            MLModelUpdate(status=ModelStatus.READY, metrics=metrics),
        )
        logger.info("Registered model '%s' (id=%s)", result["model_name"], created.id)
    finally:
        db.close()


@celery_app.task(base=TrackedTask, bind=True, name="drug_design.predict_sar")
def predict_sar_task(
    self,
    smiles_list: List[str],
    model_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Batch SAR activity prediction using the trained engine."""
    from app.ml.drug_design.inference import SARInferenceEngine

    engine = SARInferenceEngine(model_path=model_path, model_type="random_forest")
    predictions = engine.predict_activity(smiles_list, return_confidence=True)
    return {"predictions": predictions, "count": len(predictions)}


@celery_app.task(base=TrackedTask, bind=True, name="drug_design.generate_molecules")
def generate_molecules_task(
    self,
    num_molecules: int = 10,
    seed_smiles: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate candidate molecules (baseline generator; Phase 2 = generative model)."""
    from app.ml.drug_design.inference import MolecularGenerator

    generator = MolecularGenerator()
    molecules = generator.generate_random_molecules(
        num_molecules=num_molecules, seed_smiles=seed_smiles
    )
    return {"molecules": molecules, "count": len(molecules)}


@celery_app.task(base=TrackedTask, bind=True, name="drug_design.optimize_molecule")
def optimize_molecule_task(
    self,
    lead_smiles: str,
    num_analogs: int = 10,
    similarity_threshold: float = 0.7,
) -> Dict[str, Any]:
    """Generate optimized analogs of a lead molecule."""
    from app.ml.drug_design.inference import MolecularGenerator

    generator = MolecularGenerator()
    analogs = generator.optimize_molecule(
        lead_smiles=lead_smiles,
        num_analogs=num_analogs,
        similarity_threshold=similarity_threshold,
    )
    return {"analogs": analogs, "count": len(analogs)}

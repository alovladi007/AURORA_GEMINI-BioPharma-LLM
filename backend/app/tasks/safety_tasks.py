"""Celery tasks for the Safety & Toxicity module."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.celery_app import celery_app
from app.tasks.base import TrackedTask


@celery_app.task(base=TrackedTask, bind=True, name="safety.predict_admet")
def predict_admet_task(self, smiles_list: List[str]) -> Dict[str, Any]:
    """Batch ADMET prediction."""
    from app.ml.safety.inference import SafetyInferenceEngine

    engine = SafetyInferenceEngine()
    results = engine.predict_admet(smiles_list)
    return {"results": results, "count": len(results)}


@celery_app.task(base=TrackedTask, bind=True, name="safety.predict_toxicity")
def predict_toxicity_task(
    self, smiles_list: List[str], endpoints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Batch toxicity prediction."""
    from app.ml.safety.inference import SafetyInferenceEngine

    engine = SafetyInferenceEngine()
    results = engine.predict_toxicity(smiles_list, endpoints=endpoints)
    return {"results": results, "count": len(results)}


@celery_app.task(base=TrackedTask, bind=True, name="safety.screen_ddi")
def screen_ddi_task(self, drug_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
    """Screen drug–drug interactions for a list of SMILES pairs."""
    from app.ml.safety.inference import SafetyInferenceEngine

    engine = SafetyInferenceEngine()
    # JSON transport delivers pairs as lists; normalize to tuples.
    pairs = [tuple(p) for p in drug_pairs]
    results = engine.screen_ddi(pairs)
    return {"results": results, "count": len(results)}

"""Celery tasks for the Drug Repurposing module.

These wrap the DrugRepurposingEngine. Parameters are passed as a dict and
unpacked to the engine method (Phase 3 replaces these with a real KG + KGE/GNN).
"""

from __future__ import annotations

from typing import Any, Dict

from app.celery_app import celery_app
from app.tasks.base import TrackedTask


@celery_app.task(base=TrackedTask, bind=True, name="repurposing.mine_kg")
def mine_kg_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Knowledge-graph mining. `params` -> mine_knowledge_graph()."""
    from app.ml.repurposing.inference import DrugRepurposingEngine

    engine = DrugRepurposingEngine()
    return engine.mine_knowledge_graph(**params)


@celery_app.task(base=TrackedTask, bind=True, name="repurposing.predict_mechanism")
def predict_mechanism_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Mechanism-of-action prediction. `params` -> predict_mechanism()."""
    from app.ml.repurposing.inference import DrugRepurposingEngine

    engine = DrugRepurposingEngine()
    return engine.predict_mechanism(**params)


@celery_app.task(base=TrackedTask, bind=True, name="repurposing.discover_combinations")
def discover_combinations_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Combination discovery. `params` -> discover_combinations()."""
    from app.ml.repurposing.inference import DrugRepurposingEngine

    engine = DrugRepurposingEngine()
    return engine.discover_combinations(**params)

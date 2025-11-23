"""Celery tasks for drug repurposing module."""

from app.celery_app import celery_app
from app.tasks.drug_design_tasks import CallbackTask
from app.ml.repurposing.inference import (
    mine_knowledge_graph,
    predict_mechanism,
    discover_combinations,
)

@celery_app.task(base=CallbackTask, bind=True, name="repurposing.kg_mine")
def mine_kg_task(self, drug_name: str, disease: str, job_id: int = None):
    """Mine knowledge graph asynchronously."""
    return mine_knowledge_graph(drug_name, disease)

@celery_app.task(base=CallbackTask, bind=True, name="repurposing.mechanism")
def predict_mechanism_task(self, drug_name: str, disease: str, job_id: int = None):
    """Predict mechanism asynchronously."""
    return predict_mechanism(drug_name, disease)

@celery_app.task(base=CallbackTask, bind=True, name="repurposing.combinations")
def discover_combinations_task(self, disease: str, max_drugs: int = 3, job_id: int = None):
    """Discover drug combinations asynchronously."""
    return discover_combinations(disease, max_drugs)

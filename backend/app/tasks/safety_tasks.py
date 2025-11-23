"""Celery tasks for safety prediction module."""

from app.celery_app import celery_app
from app.tasks.drug_design_tasks import CallbackTask
from app.ml.safety.inference import predict_admet, predict_toxicity, screen_ddi

@celery_app.task(base=CallbackTask, bind=True, name="safety.admet")
def predict_admet_task(self, smiles: str, job_id: int = None):
    """Predict ADMET properties asynchronously."""
    return predict_admet(smiles)

@celery_app.task(base=CallbackTask, bind=True, name="safety.toxicity")
def predict_toxicity_task(self, smiles: str, job_id: int = None):
    """Predict toxicity asynchronously."""
    return predict_toxicity(smiles)

@celery_app.task(base=CallbackTask, bind=True, name="safety.ddi")
def screen_ddi_task(self, drug1_smiles: str, drug2_smiles: str, job_id: int = None):
    """Screen drug-drug interactions asynchronously."""
    return screen_ddi(drug1_smiles, drug2_smiles)

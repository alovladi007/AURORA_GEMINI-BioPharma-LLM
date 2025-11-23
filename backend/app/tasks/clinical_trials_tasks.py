"""Celery tasks for clinical trials module."""

from app.celery_app import celery_app
from app.tasks.drug_design_tasks import CallbackTask
from app.ml.clinical_trials.inference import (
    predict_patient_recruitment,
    optimize_trial_design,
    monitor_safety_signals,
)

@celery_app.task(base=CallbackTask, bind=True, name="clinical.recruit")
def recruit_patients_task(self, trial_criteria: dict, job_id: int = None):
    """Predict patient recruitment asynchronously."""
    return predict_patient_recruitment(trial_criteria)

@celery_app.task(base=CallbackTask, bind=True, name="clinical.design")
def design_trial_task(self, trial_params: dict, job_id: int = None):
    """Optimize trial design asynchronously."""
    return optimize_trial_design(trial_params)

@celery_app.task(base=CallbackTask, bind=True, name="clinical.safety")
def monitor_safety_task(self, trial_data: dict, job_id: int = None):
    """Monitor safety signals asynchronously."""
    return monitor_safety_signals(trial_data)

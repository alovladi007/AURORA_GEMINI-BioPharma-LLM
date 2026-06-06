"""Celery tasks for the Clinical Trials module.

These wrap the ClinicalTrialsEngine. Parameters are passed as a dict and unpacked
to the engine method, keeping the task layer decoupled from evolving signatures.
"""

from __future__ import annotations

from typing import Any, Dict

from app.celery_app import celery_app
from app.tasks.base import TrackedTask


@celery_app.task(base=TrackedTask, bind=True, name="clinical.recruit")
def recruit_patients_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Patient recruitment optimization. `params` -> optimize_patient_recruitment()."""
    from app.ml.clinical_trials.inference import ClinicalTrialsEngine

    engine = ClinicalTrialsEngine()
    return engine.optimize_patient_recruitment(**params)


@celery_app.task(base=TrackedTask, bind=True, name="clinical.design")
def design_trial_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Trial design optimization. `params` -> optimize_trial_design()."""
    from app.ml.clinical_trials.inference import ClinicalTrialsEngine

    engine = ClinicalTrialsEngine()
    return engine.optimize_trial_design(**params)


@celery_app.task(base=TrackedTask, bind=True, name="clinical.safety_plan")
def safety_monitoring_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Safety monitoring plan. `params` -> generate_safety_monitoring_plan()."""
    from app.ml.clinical_trials.inference import ClinicalTrialsEngine

    engine = ClinicalTrialsEngine()
    return engine.generate_safety_monitoring_plan(**params)

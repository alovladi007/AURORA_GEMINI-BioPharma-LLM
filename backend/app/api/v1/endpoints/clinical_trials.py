"""
Clinical Trials API endpoints.

Provides patient recruitment, trial design, and safety monitoring.
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.schemas.clinical_trials import (
    PatientRecruitmentRequest,
    PatientRecruitmentResponse,
    TrialDesignRequest,
    TrialDesignResponse,
    SafetyMonitoringRequest,
    SafetyMonitoringResponse,
)
from app.ml.clinical_trials.inference import ClinicalTrialsEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize global engine
_clinical_trials_engine = None


def get_clinical_trials_engine() -> ClinicalTrialsEngine:
    """Get or create clinical trials engine."""
    global _clinical_trials_engine

    if _clinical_trials_engine is None:
        logger.info("Initializing Clinical Trials engine...")
        _clinical_trials_engine = ClinicalTrialsEngine()

    return _clinical_trials_engine


@router.post("/recruit", response_model=PatientRecruitmentResponse)
def optimize_patient_recruitment(request: PatientRecruitmentRequest):
    """
    Optimize patient recruitment for clinical trials.

    **Request Parameters:**
    - **trial_name**: Name of the clinical trial
    - **indication**: Disease or condition being studied
    - **criteria**: Patient eligibility criteria (age, gender, biomarkers, etc.)
    - **target_enrollment**: Target number of patients to enroll
    - **trial_locations**: Preferred trial site locations (optional)

    **Returns:**
    - Recommended trial sites with estimated eligible patients
    - Recruitment rates and feasibility scores
    - Estimated recruitment timeline
    - Recruitment strategy recommendations

    **Example:**
    ```json
    {
        "trial_name": "Phase 3 Oncology Trial",
        "indication": "Non-Small Cell Lung Cancer",
        "criteria": {
            "age_min": 18,
            "age_max": 75,
            "disease_stage": "Stage III-IV",
            "biomarkers": ["PD-L1+"]
        },
        "target_enrollment": 300
    }
    ```
    """
    try:
        engine = get_clinical_trials_engine()

        result = engine.optimize_patient_recruitment(
            trial_name=request.trial_name,
            indication=request.indication,
            criteria=request.criteria.model_dump(exclude_none=True),
            target_enrollment=request.target_enrollment,
            trial_locations=request.trial_locations,
        )

        return PatientRecruitmentResponse(**result)

    except Exception as e:
        logger.error(f"Error optimizing patient recruitment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize recruitment: {str(e)}"
        )


@router.post("/design", response_model=TrialDesignResponse)
def optimize_trial_design(request: TrialDesignRequest):
    """
    Optimize clinical trial design.

    **Request Parameters:**
    - **trial_type**: Type of trial (phase1, phase2, phase3)
    - **indication**: Disease or condition
    - **intervention**: Drug or intervention being tested
    - **primary_endpoint**: Primary efficacy endpoint
    - **secondary_endpoints**: Secondary endpoints (optional)
    - **target_enrollment**: Target sample size
    - **treatment_duration_weeks**: Duration of treatment

    **Returns:**
    - Recommended trial design (randomization, blinding)
    - Trial arms configuration
    - Power analysis and sample size justification
    - Statistical considerations
    - Estimated trial duration

    **Example:**
    ```json
    {
        "trial_type": "phase3",
        "indication": "Type 2 Diabetes",
        "intervention": "Novel GLP-1 Agonist",
        "primary_endpoint": "HbA1c reduction at 24 weeks",
        "secondary_endpoints": ["Weight loss", "Fasting glucose"],
        "target_enrollment": 500,
        "treatment_duration_weeks": 24
    }
    ```
    """
    try:
        engine = get_clinical_trials_engine()

        result = engine.optimize_trial_design(
            trial_type=request.trial_type,
            indication=request.indication,
            intervention=request.intervention,
            primary_endpoint=request.primary_endpoint,
            secondary_endpoints=request.secondary_endpoints,
            target_enrollment=request.target_enrollment,
            treatment_duration_weeks=request.treatment_duration_weeks,
        )

        return TrialDesignResponse(**result)

    except Exception as e:
        logger.error(f"Error optimizing trial design: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize trial design: {str(e)}"
        )


@router.post("/safety-monitoring", response_model=SafetyMonitoringResponse)
def generate_safety_monitoring_plan(request: SafetyMonitoringRequest):
    """
    Generate safety monitoring plan for clinical trial.

    **Request Parameters:**
    - **trial_id**: Trial identifier
    - **intervention**: Drug or intervention being tested
    - **patient_population**: Description of patient population
    - **known_safety_concerns**: Known safety issues (optional)

    **Returns:**
    - Recommended safety metrics to monitor
    - Monitoring frequency and alert thresholds
    - Stopping rules for the trial
    - DSMB (Data Safety Monitoring Board) recommendations

    **Example:**
    ```json
    {
        "trial_id": "NCT12345678",
        "intervention": "Novel Kinase Inhibitor",
        "patient_population": "Advanced cancer patients",
        "known_safety_concerns": ["Hepatotoxicity", "QT prolongation"]
    }
    ```
    """
    try:
        engine = get_clinical_trials_engine()

        result = engine.generate_safety_monitoring_plan(
            trial_id=request.trial_id,
            intervention=request.intervention,
            patient_population=request.patient_population,
            known_safety_concerns=request.known_safety_concerns,
        )

        return SafetyMonitoringResponse(**result)

    except Exception as e:
        logger.error(f"Error generating safety monitoring plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate safety monitoring plan: {str(e)}"
        )

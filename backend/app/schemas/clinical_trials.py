"""
Clinical Trials schemas.

Request/response schemas for clinical trial optimization endpoints.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# Patient Recruitment
class PatientCriteria(BaseModel):
    """Patient eligibility criteria."""
    age_min: Optional[int] = Field(None, ge=0, le=120, description="Minimum age")
    age_max: Optional[int] = Field(None, ge=0, le=120, description="Maximum age")
    gender: Optional[str] = Field(None, description="Gender requirement (M/F/All)")
    disease_stage: Optional[str] = Field(None, description="Disease stage")
    biomarkers: Optional[List[str]] = Field(None, description="Required biomarkers")
    exclusion_criteria: Optional[List[str]] = Field(None, description="Exclusion criteria")


class PatientRecruitmentRequest(BaseModel):
    """Request for patient recruitment optimization."""
    trial_name: str = Field(..., description="Trial name")
    indication: str = Field(..., description="Disease/indication")
    criteria: PatientCriteria
    target_enrollment: int = Field(..., ge=1, description="Target number of patients")
    trial_locations: Optional[List[str]] = Field(None, description="Trial site locations")


class RecruitmentSite(BaseModel):
    """Recruitment site information."""
    location: str
    estimated_eligible_patients: int
    recruitment_rate: float = Field(..., ge=0, le=1, description="Monthly recruitment rate")
    site_feasibility_score: float = Field(..., ge=0, le=1)


class PatientRecruitmentResponse(BaseModel):
    """Response for patient recruitment optimization."""
    trial_name: str
    indication: str
    total_estimated_eligible: int
    recommended_sites: List[RecruitmentSite]
    estimated_recruitment_time_months: float
    recruitment_strategy: str
    feasibility_score: float = Field(..., ge=0, le=1)


# Trial Design
class TrialDesignRequest(BaseModel):
    """Request for trial design optimization."""
    trial_type: str = Field(..., description="Trial type (phase1/phase2/phase3)")
    indication: str
    intervention: str = Field(..., description="Drug/intervention being tested")
    primary_endpoint: str
    secondary_endpoints: Optional[List[str]] = None
    target_enrollment: int = Field(..., ge=1)
    treatment_duration_weeks: int = Field(..., ge=1)


class TrialArm(BaseModel):
    """Trial arm configuration."""
    arm_name: str
    description: str
    sample_size: int
    treatment: str


class TrialDesignResponse(BaseModel):
    """Response for trial design optimization."""
    trial_type: str
    indication: str
    recommended_design: str = Field(..., description="Recommended trial design type")
    trial_arms: List[TrialArm]
    total_sample_size: int
    estimated_duration_months: float
    power_analysis: Dict[str, Any]
    statistical_considerations: List[str]


# Safety Monitoring
class SafetyMonitoringRequest(BaseModel):
    """Request for safety monitoring recommendations."""
    trial_id: str
    intervention: str
    patient_population: str
    known_safety_concerns: Optional[List[str]] = None


class SafetyMetric(BaseModel):
    """Safety metric to monitor."""
    metric_name: str
    monitoring_frequency: str
    alert_threshold: str
    severity: str = Field(..., description="low/moderate/high")


class SafetyMonitoringResponse(BaseModel):
    """Response for safety monitoring recommendations."""
    trial_id: str
    recommended_metrics: List[SafetyMetric]
    monitoring_schedule: str
    stopping_rules: List[str]
    dsmb_recommendations: List[str] = Field(..., description="Data Safety Monitoring Board recommendations")

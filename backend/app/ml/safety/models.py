"""
Safety & Toxicity prediction models.

Models for ADMET prediction, toxicity assessment, and drug-drug interactions.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import logging

# Use the same base predictors from drug_design
from app.ml.drug_design.models import RandomForestSARPredictor

logger = logging.getLogger(__name__)


class ADMETPredictor:
    """
    ADMET property predictor.

    Predicts Absorption, Distribution, Metabolism, Excretion, and Toxicity properties.
    """

    def __init__(self):
        """Initialize ADMET predictor with multiple models."""
        # In production, these would be separate trained models for each property
        # For now, use simple rule-based predictions combined with descriptors
        self.models = {}

    def predict_admet(self, descriptors: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict ADMET properties from molecular descriptors.

        Args:
            descriptors: Dictionary of molecular descriptors

        Returns:
            Dictionary with ADMET predictions
        """
        # Absorption predictions
        absorption = {
            "Caco2": self._predict_caco2(descriptors),
            "HIA": self._predict_hia(descriptors),  # Human Intestinal Absorption
            "bioavailability": self._predict_bioavailability(descriptors),
        }

        # Distribution predictions
        distribution = {
            "BBB": self._predict_bbb(descriptors),  # Blood-Brain Barrier
            "PPB": self._predict_ppb(descriptors),  # Plasma Protein Binding
            "VDss": self._predict_vdss(descriptors),  # Volume of Distribution
        }

        # Metabolism predictions
        metabolism = {
            "CYP3A4_substrate": self._predict_cyp_substrate(descriptors, "3A4"),
            "CYP2D6_substrate": self._predict_cyp_substrate(descriptors, "2D6"),
            "CYP2C9_substrate": self._predict_cyp_substrate(descriptors, "2C9"),
        }

        # Excretion predictions
        excretion = {
            "half_life": self._predict_half_life(descriptors),
            "clearance": self._predict_clearance(descriptors),
        }

        # Toxicity predictions (basic)
        toxicity = {
            "hERG": self._predict_herg(descriptors),
            "hepatotoxicity": self._predict_hepatotoxicity(descriptors),
            "AMES": self._predict_ames(descriptors),
        }

        # Overall ADMET score (0-1, higher is better)
        overall_score = self._compute_overall_score(absorption, distribution, metabolism, excretion, toxicity)

        return {
            "absorption": absorption,
            "distribution": distribution,
            "metabolism": metabolism,
            "excretion": excretion,
            "toxicity": toxicity,
            "overall_score": overall_score,
        }

    def _predict_caco2(self, desc: Dict[str, float]) -> float:
        """Predict Caco-2 permeability (higher is better)."""
        # Simple rule: lower TPSA and moderate LogP = better permeability
        tpsa = desc.get("tpsa", 100)
        logp = desc.get("logP", 0)

        # Normalize to 0-1
        score = max(0, min(1, (140 - tpsa) / 140)) * 0.7 + max(0, min(1, (5 - abs(logp - 2.5)) / 5)) * 0.3
        return round(score, 3)

    def _predict_hia(self, desc: Dict[str, float]) -> float:
        """Predict Human Intestinal Absorption (0-1, higher is better)."""
        # Good absorption: MW < 500, TPSA < 140, moderate LogP
        mw = desc.get("molecular_weight", 500)
        tpsa = desc.get("tpsa", 100)

        score = max(0, min(1, (600 - mw) / 600)) * 0.5 + max(0, min(1, (140 - tpsa) / 140)) * 0.5
        return round(score, 3)

    def _predict_bioavailability(self, desc: Dict[str, float]) -> float:
        """Predict oral bioavailability (0-1)."""
        # Based on Lipinski's Rule of Five
        ro5_violations = 0

        if desc.get("molecular_weight", 0) > 500:
            ro5_violations += 1
        if desc.get("logP", 0) > 5:
            ro5_violations += 1
        if desc.get("num_h_donors", 0) > 5:
            ro5_violations += 1
        if desc.get("num_h_acceptors", 0) > 10:
            ro5_violations += 1

        score = max(0, 1.0 - (ro5_violations * 0.25))
        return round(score, 3)

    def _predict_bbb(self, desc: Dict[str, float]) -> float:
        """Predict Blood-Brain Barrier penetration (0-1)."""
        # Low TPSA and moderate LogP favor BBB penetration
        tpsa = desc.get("tpsa", 100)
        logp = desc.get("logP", 0)

        if tpsa > 90:
            return 0.1  # Unlikely to cross
        else:
            score = max(0, min(1, (90 - tpsa) / 90)) * 0.6 + max(0, min(1, abs(logp - 2.0) / 5)) * 0.4
            return round(score, 3)

    def _predict_ppb(self, desc: Dict[str, float]) -> float:
        """Predict Plasma Protein Binding (0-1, fraction bound)."""
        # Higher LogP generally means more protein binding
        logp = desc.get("logP", 0)
        score = min(0.99, max(0.1, (logp + 2) / 7))
        return round(score, 3)

    def _predict_vdss(self, desc: Dict[str, float]) -> float:
        """Predict Volume of Distribution at steady state (L/kg)."""
        # Rough estimate based on LogP and MW
        logp = desc.get("logP", 0)
        mw = desc.get("molecular_weight", 300)

        vdss = 0.5 + (logp * 0.3) + (mw / 1000)
        return round(max(0.1, min(10.0, vdss)), 2)

    def _predict_cyp_substrate(self, desc: Dict[str, float], cyp_type: str) -> float:
        """Predict if molecule is CYP substrate (0-1 probability)."""
        # Simple heuristic based on molecular properties
        mw = desc.get("molecular_weight", 300)
        logp = desc.get("logP", 0)

        # Moderate MW and LogP more likely to be substrates
        if 200 < mw < 600 and 0 < logp < 5:
            prob = 0.6 + np.random.uniform(-0.2, 0.2)  # Add some variability
        else:
            prob = 0.3 + np.random.uniform(-0.1, 0.1)

        return round(max(0, min(1, prob)), 3)

    def _predict_half_life(self, desc: Dict[str, float]) -> float:
        """Predict elimination half-life (hours)."""
        # Rough estimate: larger, more lipophilic molecules have longer half-lives
        mw = desc.get("molecular_weight", 300)
        logp = desc.get("logP", 0)

        half_life = 2 + (mw / 100) + (logp * 0.5)
        return round(max(0.5, min(24, half_life)), 2)

    def _predict_clearance(self, desc: Dict[str, float]) -> float:
        """Predict clearance (mL/min/kg)."""
        # Inversely related to half-life
        half_life = self._predict_half_life(desc)
        clearance = 20 / (half_life + 1)
        return round(max(1, min(50, clearance)), 2)

    def _predict_herg(self, desc: Dict[str, float]) -> float:
        """Predict hERG inhibition risk (0-1, higher is more risky)."""
        # Structural alerts for hERG: basic nitrogen, aromatic rings, lipophilicity
        logp = desc.get("logP", 0)
        aromatic_rings = desc.get("num_aromatic_rings", 0)

        risk = 0.2  # Baseline
        if logp > 3:
            risk += 0.3
        if aromatic_rings >= 2:
            risk += 0.2

        return round(min(1.0, risk), 3)

    def _predict_hepatotoxicity(self, desc: Dict[str, float]) -> float:
        """Predict hepatotoxicity risk (0-1)."""
        # Higher MW and certain functional groups increase risk
        mw = desc.get("molecular_weight", 300)

        risk = 0.1  # Baseline
        if mw > 600:
            risk += 0.3
        if desc.get("num_aromatic_rings", 0) > 3:
            risk += 0.2

        return round(min(1.0, risk), 3)

    def _predict_ames(self, desc: Dict[str, float]) -> float:
        """Predict AMES mutagenicity (0-1, higher is more mutagenic)."""
        # Structural alerts for mutagenicity
        aromatic_rings = desc.get("num_aromatic_rings", 0)

        risk = 0.05  # Baseline
        if aromatic_rings >= 3:
            risk += 0.4

        return round(min(1.0, risk), 3)

    def _compute_overall_score(
        self,
        absorption: Dict,
        distribution: Dict,
        metabolism: Dict,
        excretion: Dict,
        toxicity: Dict
    ) -> float:
        """Compute overall ADMET score (0-1, higher is better)."""
        # Weighted average of favorable properties
        score = 0.0

        # Absorption (higher is better)
        score += absorption.get("Caco2", 0) * 0.1
        score += absorption.get("HIA", 0) * 0.1
        score += absorption.get("bioavailability", 0) * 0.15

        # Distribution (moderate is better)
        score += min(distribution.get("BBB", 0), 0.5) * 0.05  # Not too high BBB

        # Toxicity (lower is better, so invert)
        score += (1 - toxicity.get("hERG", 0)) * 0.2
        score += (1 - toxicity.get("hepatotoxicity", 0)) * 0.2
        score += (1 - toxicity.get("AMES", 0)) * 0.2

        return round(score, 3)


class ToxicityPredictor:
    """
    Toxicity endpoint predictor.

    Predicts various toxicity endpoints (hepatotoxicity, cardiotoxicity, etc.).
    """

    ENDPOINTS = [
        "hepatotoxicity",
        "cardiotoxicity",
        "nephrotoxicity",
        "neurotoxicity",
        "genotoxicity",
        "carcinogenicity",
        "skin_sensitization",
    ]

    def __init__(self):
        """Initialize toxicity predictor."""
        pass

    def predict_toxicity(
        self,
        descriptors: Dict[str, float],
        endpoints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Predict toxicity for specified endpoints.

        Args:
            descriptors: Molecular descriptors
            endpoints: List of endpoints to predict (or all if None)

        Returns:
            Dictionary with toxicity predictions
        """
        if endpoints is None:
            endpoints = self.ENDPOINTS

        predictions = {}

        for endpoint in endpoints:
            prob = self._predict_endpoint(endpoint, descriptors)
            risk_level = self._get_risk_level(prob)

            predictions[endpoint] = {
                "probability": prob,
                "risk_level": risk_level,
                "confidence": 0.75,  # Placeholder confidence
            }

        # Overall risk (max of all endpoints)
        overall_prob = max([p["probability"] for p in predictions.values()])
        overall_risk = self._get_risk_level(overall_prob)

        return {
            "endpoints": predictions,
            "overall_risk": overall_risk,
            "overall_probability": overall_prob,
        }

    def _predict_endpoint(self, endpoint: str, desc: Dict[str, float]) -> float:
        """Predict toxicity for a specific endpoint."""
        # Simple rule-based predictions
        # In production, use trained ML models

        mw = desc.get("molecular_weight", 300)
        logp = desc.get("logP", 0)
        aromatic_rings = desc.get("num_aromatic_rings", 0)
        tpsa = desc.get("tpsa", 50)

        base_prob = 0.1

        if endpoint == "hepatotoxicity":
            if mw > 500:
                base_prob += 0.3
            if aromatic_rings > 2:
                base_prob += 0.2

        elif endpoint == "cardiotoxicity":
            if logp > 4:
                base_prob += 0.3
            if aromatic_rings >= 2:
                base_prob += 0.2

        elif endpoint == "nephrotoxicity":
            if mw > 600:
                base_prob += 0.3

        elif endpoint == "neurotoxicity":
            if tpsa < 60:  # Can cross BBB
                base_prob += 0.2

        elif endpoint == "genotoxicity":
            if aromatic_rings >= 3:
                base_prob += 0.4

        elif endpoint == "carcinogenicity":
            if aromatic_rings >= 3:
                base_prob += 0.35

        elif endpoint == "skin_sensitization":
            if aromatic_rings >= 2:
                base_prob += 0.25

        return round(min(1.0, base_prob), 3)

    def _get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level."""
        if probability < 0.3:
            return "low"
        elif probability < 0.7:
            return "moderate"
        else:
            return "high"

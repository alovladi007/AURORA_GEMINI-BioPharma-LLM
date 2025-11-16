"""
Inference utilities for Safety & Toxicity module.

Provides high-level interface for ADMET prediction, toxicity assessment, and DDI screening.
"""

from typing import List, Dict, Optional, Any
import logging

from app.ml.common.featurization import MolecularFeaturizer
from app.ml.safety.models import ADMETPredictor, ToxicityPredictor

logger = logging.getLogger(__name__)


class SafetyInferenceEngine:
    """
    Inference engine for safety and toxicity predictions.
    """

    def __init__(self):
        """Initialize safety inference engine."""
        self.featurizer = MolecularFeaturizer()
        self.admet_predictor = ADMETPredictor()
        self.toxicity_predictor = ToxicityPredictor()

    def predict_admet(self, smiles_list: List[str]) -> List[Dict[str, Any]]:
        """
        Predict ADMET properties for molecules.

        Args:
            smiles_list: List of SMILES strings

        Returns:
            List of ADMET predictions
        """
        results = []

        for smiles in smiles_list:
            # Compute descriptors
            descriptors = self.featurizer.compute_descriptors(smiles)

            if descriptors is None:
                results.append({
                    "smiles": smiles,
                    "error": "Invalid SMILES"
                })
                continue

            # Predict ADMET
            admet_pred = self.admet_predictor.predict_admet(descriptors)

            results.append({
                "smiles": smiles,
                **admet_pred
            })

        return results

    def predict_toxicity(
        self,
        smiles_list: List[str],
        endpoints: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict toxicity endpoints for molecules.

        Args:
            smiles_list: List of SMILES strings
            endpoints: Specific endpoints to predict (or all if None)

        Returns:
            List of toxicity predictions
        """
        results = []

        for smiles in smiles_list:
            # Compute descriptors
            descriptors = self.featurizer.compute_descriptors(smiles)

            if descriptors is None:
                results.append({
                    "smiles": smiles,
                    "error": "Invalid SMILES"
                })
                continue

            # Predict toxicity
            tox_pred = self.toxicity_predictor.predict_toxicity(descriptors, endpoints)

            # Get structural alerts (simple heuristics)
            alerts = self._get_structural_alerts(descriptors)

            results.append({
                "smiles": smiles,
                "endpoints": [
                    {
                        "endpoint": endpoint,
                        **pred_data
                    }
                    for endpoint, pred_data in tox_pred["endpoints"].items()
                ],
                "overall_risk": tox_pred["overall_risk"],
                "alerts": alerts
            })

        return results

    def screen_ddi(self, drug_pairs: List[tuple]) -> List[Dict[str, Any]]:
        """
        Screen for drug-drug interactions.

        Args:
            drug_pairs: List of (drug1_smiles, drug2_smiles) tuples

        Returns:
            List of DDI predictions
        """
        results = []

        for drug1_smiles, drug2_smiles in drug_pairs:
            # Compute descriptors for both drugs
            desc1 = self.featurizer.compute_descriptors(drug1_smiles)
            desc2 = self.featurizer.compute_descriptors(drug2_smiles)

            if desc1 is None or desc2 is None:
                results.append({
                    "drug1_smiles": drug1_smiles,
                    "drug2_smiles": drug2_smiles,
                    "error": "Invalid SMILES"
                })
                continue

            # Predict DDI (simple heuristic)
            ddi_pred = self._predict_ddi(desc1, desc2)

            results.append({
                "drug1_smiles": drug1_smiles,
                "drug2_smiles": drug2_smiles,
                **ddi_pred
            })

        return results

    def _get_structural_alerts(self, descriptors: Dict[str, float]) -> List[str]:
        """Get structural alerts based on molecular properties."""
        alerts = []

        if descriptors.get("molecular_weight", 0) > 600:
            alerts.append("High molecular weight (>600 Da)")

        if descriptors.get("logP", 0) > 5:
            alerts.append("High lipophilicity (LogP > 5)")

        if descriptors.get("num_aromatic_rings", 0) >= 3:
            alerts.append("Multiple aromatic rings (>=3)")

        if descriptors.get("num_h_donors", 0) > 5:
            alerts.append("Many H-bond donors (>5)")

        if descriptors.get("num_rotatable_bonds", 0) > 10:
            alerts.append("Highly flexible (>10 rotatable bonds)")

        return alerts

    def _predict_ddi(self, desc1: Dict[str, float], desc2: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict drug-drug interaction.

        Simple heuristic: check for similar metabolism pathways and properties.
        """
        # Check if both are likely CYP substrates (competitive inhibition risk)
        cyp_risk = 0.0

        mw1, mw2 = desc1.get("molecular_weight", 0), desc2.get("molecular_weight", 0)
        logp1, logp2 = desc1.get("logP", 0), desc2.get("logP", 0)

        # Both in similar MW and LogP range = likely same metabolism pathway
        if abs(mw1 - mw2) < 200 and abs(logp1 - logp2) < 2:
            cyp_risk = 0.6

        # Both lipophilic = P-gp interaction risk
        if logp1 > 3 and logp2 > 3:
            cyp_risk = max(cyp_risk, 0.5)

        # Determine risk level
        if cyp_risk < 0.3:
            risk_level = "low"
            mechanism = "No major interaction predicted"
            recommendation = "No special monitoring required"
        elif cyp_risk < 0.7:
            risk_level = "moderate"
            mechanism = "Possible CYP enzyme competition or P-gp interaction"
            recommendation = "Monitor patient for adverse effects or reduced efficacy"
        else:
            risk_level = "high"
            mechanism = "Likely CYP enzyme competition or significant pharmacokinetic interaction"
            recommendation = "Consider alternative therapy or close monitoring with dose adjustment"

        return {
            "interaction_probability": round(cyp_risk, 3),
            "risk_level": risk_level,
            "mechanism": mechanism,
            "recommendation": recommendation
        }

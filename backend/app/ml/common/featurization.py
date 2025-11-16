"""
Molecular featurization using RDKit.

Provides utilities for computing molecular fingerprints, descriptors,
and other features for machine learning.
"""

from typing import List, Optional, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Import RDKit components
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, Crippen, Lipinski, QED
    from rdkit.Chem import MACCSkeys
    from rdkit import DataStructs
    RDKIT_AVAILABLE = True
except ImportError:
    logger.warning("RDKit not installed. Molecular featurization will not work.")
    RDKIT_AVAILABLE = False


class MolecularFeaturizer:
    """
    Molecular featurization using RDKit.

    Supports multiple fingerprint types and molecular descriptors.
    """

    FINGERPRINT_TYPES = ["morgan", "maccs", "rdkit", "atompair", "topological"]

    @staticmethod
    def smiles_to_mol(smiles: str) -> Optional[Any]:
        """
        Convert SMILES to RDKit molecule object.

        Args:
            smiles: SMILES string

        Returns:
            RDKit Mol object or None if invalid
        """
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit is required for molecular featurization")

        return Chem.MolFromSmiles(smiles)

    @staticmethod
    def compute_morgan_fingerprint(
        smiles: str,
        radius: int = 2,
        n_bits: int = 2048,
        use_features: bool = False
    ) -> Optional[np.ndarray]:
        """
        Compute Morgan (circular) fingerprint.

        Args:
            smiles: SMILES string
            radius: Fingerprint radius (default: 2)
            n_bits: Number of bits (default: 2048)
            use_features: Use feature-based version (FCFP)

        Returns:
            Binary fingerprint as numpy array or None if invalid
        """
        mol = MolecularFeaturizer.smiles_to_mol(smiles)
        if mol is None:
            return None

        fp = AllChem.GetMorganFingerprintAsBitVect(
            mol,
            radius=radius,
            nBits=n_bits,
            useFeatures=use_features
        )

        # Convert to numpy array
        arr = np.zeros((n_bits,), dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)

        return arr

    @staticmethod
    def compute_maccs_fingerprint(smiles: str) -> Optional[np.ndarray]:
        """
        Compute MACCS keys fingerprint (166 bits).

        Args:
            smiles: SMILES string

        Returns:
            Binary fingerprint as numpy array or None if invalid
        """
        mol = MolecularFeaturizer.smiles_to_mol(smiles)
        if mol is None:
            return None

        fp = MACCSkeys.GenMACCSKeys(mol)

        # Convert to numpy array
        arr = np.zeros((166,), dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)

        return arr

    @staticmethod
    def compute_rdkit_fingerprint(smiles: str, n_bits: int = 2048) -> Optional[np.ndarray]:
        """
        Compute RDKit topological fingerprint.

        Args:
            smiles: SMILES string
            n_bits: Number of bits (default: 2048)

        Returns:
            Binary fingerprint as numpy array or None if invalid
        """
        mol = MolecularFeaturizer.smiles_to_mol(smiles)
        if mol is None:
            return None

        fp = Chem.RDKFingerprint(mol, fpSize=n_bits)

        # Convert to numpy array
        arr = np.zeros((n_bits,), dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)

        return arr

    @staticmethod
    def compute_fingerprint(
        smiles: str,
        fp_type: str = "morgan",
        **kwargs
    ) -> Optional[np.ndarray]:
        """
        Compute molecular fingerprint of specified type.

        Args:
            smiles: SMILES string
            fp_type: Fingerprint type ("morgan", "maccs", "rdkit", etc.)
            **kwargs: Additional arguments for fingerprint computation

        Returns:
            Fingerprint as numpy array or None if invalid
        """
        if fp_type == "morgan":
            return MolecularFeaturizer.compute_morgan_fingerprint(smiles, **kwargs)
        elif fp_type == "maccs":
            return MolecularFeaturizer.compute_maccs_fingerprint(smiles)
        elif fp_type == "rdkit":
            return MolecularFeaturizer.compute_rdkit_fingerprint(smiles, **kwargs)
        else:
            raise ValueError(f"Unknown fingerprint type: {fp_type}")

    @staticmethod
    def compute_descriptors(smiles: str) -> Optional[Dict[str, float]]:
        """
        Compute common molecular descriptors.

        Args:
            smiles: SMILES string

        Returns:
            Dictionary of descriptor values or None if invalid
        """
        mol = MolecularFeaturizer.smiles_to_mol(smiles)
        if mol is None:
            return None

        descriptors = {
            # Basic properties
            "molecular_weight": Descriptors.MolWt(mol),
            "num_atoms": mol.GetNumAtoms(),
            "num_heavy_atoms": Descriptors.HeavyAtomCount(mol),
            "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
            "num_h_donors": Descriptors.NumHDonors(mol),
            "num_h_acceptors": Descriptors.NumHAcceptors(mol),
            "num_rings": Descriptors.RingCount(mol),
            "num_aromatic_rings": Descriptors.NumAromaticRings(mol),

            # Lipinski's Rule of Five
            "logP": Crippen.MolLogP(mol),
            "molar_refractivity": Crippen.MolMR(mol),

            # TPSA (Topological Polar Surface Area)
            "tpsa": Descriptors.TPSA(mol),

            # QED (Quantitative Estimate of Drug-likeness)
            "qed": QED.qed(mol),

            # Additional properties
            "num_aliphatic_carbocycles": Descriptors.NumAliphaticCarbocycles(mol),
            "num_aliphatic_heterocycles": Descriptors.NumAliphaticHeterocycles(mol),
            "num_aromatic_carbocycles": Descriptors.NumAromaticCarbocycles(mol),
            "num_aromatic_heterocycles": Descriptors.NumAromaticHeterocycles(mol),
            "num_saturated_carbocycles": Descriptors.NumSaturatedCarbocycles(mol),
            "num_saturated_heterocycles": Descriptors.NumSaturatedHeterocycles(mol),

            # Charge and polarity
            "fraction_csp3": Descriptors.FractionCsp3(mol),
            "num_valence_electrons": Descriptors.NumValenceElectrons(mol),
        }

        return descriptors

    @staticmethod
    def compute_descriptor_vector(smiles: str) -> Optional[np.ndarray]:
        """
        Compute molecular descriptors as a feature vector.

        Args:
            smiles: SMILES string

        Returns:
            Descriptor vector as numpy array or None if invalid
        """
        descriptors = MolecularFeaturizer.compute_descriptors(smiles)
        if descriptors is None:
            return None

        # Convert to ordered array
        return np.array(list(descriptors.values()), dtype=np.float32)

    @staticmethod
    def check_lipinski_rule_of_five(smiles: str) -> Optional[Dict[str, bool]]:
        """
        Check Lipinski's Rule of Five for drug-likeness.

        Args:
            smiles: SMILES string

        Returns:
            Dictionary with rule violations or None if invalid
        """
        mol = MolecularFeaturizer.smiles_to_mol(smiles)
        if mol is None:
            return None

        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        return {
            "molecular_weight_ok": mw <= 500,
            "logP_ok": logp <= 5,
            "h_donors_ok": hbd <= 5,
            "h_acceptors_ok": hba <= 10,
            "passes_ro5": (mw <= 500) and (logp <= 5) and (hbd <= 5) and (hba <= 10)
        }

    @staticmethod
    def compute_tanimoto_similarity(smiles1: str, smiles2: str, fp_type: str = "morgan") -> Optional[float]:
        """
        Compute Tanimoto similarity between two molecules.

        Args:
            smiles1: First SMILES string
            smiles2: Second SMILES string
            fp_type: Fingerprint type to use

        Returns:
            Tanimoto similarity (0-1) or None if invalid
        """
        fp1 = MolecularFeaturizer.compute_fingerprint(smiles1, fp_type=fp_type)
        fp2 = MolecularFeaturizer.compute_fingerprint(smiles2, fp_type=fp_type)

        if fp1 is None or fp2 is None:
            return None

        # Convert to RDKit bit vectors for Tanimoto calculation
        mol1 = MolecularFeaturizer.smiles_to_mol(smiles1)
        mol2 = MolecularFeaturizer.smiles_to_mol(smiles2)

        if fp_type == "morgan":
            fp1_bv = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
            fp2_bv = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
        elif fp_type == "maccs":
            fp1_bv = MACCSkeys.GenMACCSKeys(mol1)
            fp2_bv = MACCSkeys.GenMACCSKeys(mol2)
        else:
            fp1_bv = Chem.RDKFingerprint(mol1)
            fp2_bv = Chem.RDKFingerprint(mol2)

        return DataStructs.TanimotoSimilarity(fp1_bv, fp2_bv)

    @staticmethod
    def batch_featurize(
        smiles_list: List[str],
        method: str = "morgan",
        **kwargs
    ) -> np.ndarray:
        """
        Featurize a batch of SMILES strings.

        Args:
            smiles_list: List of SMILES strings
            method: Featurization method ("morgan", "maccs", "rdkit", "descriptors")
            **kwargs: Additional arguments for featurization

        Returns:
            Feature matrix (n_molecules, n_features)
        """
        features = []

        for smiles in smiles_list:
            if method in MolecularFeaturizer.FINGERPRINT_TYPES:
                feat = MolecularFeaturizer.compute_fingerprint(smiles, fp_type=method, **kwargs)
            elif method == "descriptors":
                feat = MolecularFeaturizer.compute_descriptor_vector(smiles)
            else:
                raise ValueError(f"Unknown featurization method: {method}")

            if feat is not None:
                features.append(feat)
            else:
                # Use zero vector for invalid SMILES
                if method == "descriptors":
                    features.append(np.zeros(20, dtype=np.float32))  # Number of descriptors
                else:
                    n_bits = kwargs.get("n_bits", 2048) if method != "maccs" else 166
                    features.append(np.zeros(n_bits, dtype=np.int8))

        return np.array(features)

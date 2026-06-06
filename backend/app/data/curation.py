"""
Dataset curation for molecular bioactivity data.

Standardizes SMILES, removes invalid/duplicate molecules, derives a binary
activity label from pChEMBL values, and writes a model-ready CSV.

RDKit is imported lazily so this module can be imported without it installed.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Standard activity threshold: pChEMBL >= 6.0 (IC50 <= 1 uM) = "active".
DEFAULT_PCHEMBL_THRESHOLD = 6.0


def canonicalize_smiles(smiles: str) -> Optional[str]:
    """Return RDKit canonical SMILES, or None if the molecule is invalid."""
    from rdkit import Chem  # lazy import

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True)


def curate_activity_records(
    records: List[Dict],
    pchembl_threshold: float = DEFAULT_PCHEMBL_THRESHOLD,
) -> List[Dict]:
    """
    Curate raw ChEMBL activity records into clean labeled rows.

    Steps:
      1. Keep rows with a parseable pChEMBL value and SMILES.
      2. Canonicalize SMILES (drops invalid molecules).
      3. Deduplicate by canonical SMILES, averaging pChEMBL across measurements.
      4. Derive binary label from the averaged pChEMBL value.

    Returns list of dicts: {smiles, pchembl_value, label}.
    """
    # 1 + 2: parse, canonicalize
    cleaned: Dict[str, List[float]] = {}
    invalid = 0
    for rec in records:
        raw_smiles = rec.get("canonical_smiles")
        pchembl = rec.get("pchembl_value")
        if raw_smiles is None or pchembl is None:
            continue
        try:
            pchembl_f = float(pchembl)
        except (TypeError, ValueError):
            continue

        canon = canonicalize_smiles(raw_smiles)
        if canon is None:
            invalid += 1
            continue

        cleaned.setdefault(canon, []).append(pchembl_f)

    # 3 + 4: dedupe by averaging, then label
    curated: List[Dict] = []
    for smiles, values in cleaned.items():
        avg = sum(values) / len(values)
        curated.append(
            {
                "smiles": smiles,
                "pchembl_value": round(avg, 3),
                "label": int(avg >= pchembl_threshold),
            }
        )

    n_active = sum(r["label"] for r in curated)
    logger.info(
        "Curated %d unique molecules (%d active / %d inactive); dropped %d invalid",
        len(curated), n_active, len(curated) - n_active, invalid,
    )
    return curated


def write_dataset_csv(curated: List[Dict], output_path: str) -> None:
    """Write curated rows to a CSV with columns: smiles, pchembl_value, label."""
    import csv
    import os

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["smiles", "pchembl_value", "label"])
        writer.writeheader()
        writer.writerows(curated)
    logger.info("Wrote %d rows to %s", len(curated), output_path)

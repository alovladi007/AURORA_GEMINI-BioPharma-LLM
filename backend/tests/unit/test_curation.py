"""
Unit tests for bioactivity data curation.

Requires RDKit (installed via requirements.txt in CI).
"""

import pytest

pytest.importorskip("rdkit")

from app.data.curation import (
    canonicalize_smiles,
    curate_activity_records,
    DEFAULT_PCHEMBL_THRESHOLD,
)


def test_canonicalize_valid_smiles():
    # Two equivalent encodings of ethanol should canonicalize identically.
    assert canonicalize_smiles("CCO") == canonicalize_smiles("OCC")


def test_canonicalize_invalid_returns_none():
    assert canonicalize_smiles("not_a_molecule") is None


def test_curation_labels_by_threshold():
    records = [
        {"canonical_smiles": "CCO", "pchembl_value": 7.5},   # active
        {"canonical_smiles": "c1ccccc1", "pchembl_value": 4.0},  # inactive
    ]
    curated = curate_activity_records(records)
    labels = {r["smiles"]: r["label"] for r in curated}
    # Active molecule (>= threshold) labeled 1, inactive labeled 0.
    assert any(v == 1 for v in labels.values())
    assert any(v == 0 for v in labels.values())


def test_curation_deduplicates_and_averages():
    # Same molecule measured twice -> single curated row with averaged pChEMBL.
    records = [
        {"canonical_smiles": "CCO", "pchembl_value": 5.0},
        {"canonical_smiles": "OCC", "pchembl_value": 7.0},  # same molecule
    ]
    curated = curate_activity_records(records)
    assert len(curated) == 1
    assert curated[0]["pchembl_value"] == pytest.approx(6.0)
    # avg 6.0 >= default threshold 6.0 -> active
    assert curated[0]["label"] == 1


def test_curation_drops_invalid_and_missing():
    records = [
        {"canonical_smiles": "not_a_mol", "pchembl_value": 9.0},
        {"canonical_smiles": "CCO", "pchembl_value": None},
        {"canonical_smiles": None, "pchembl_value": 8.0},
    ]
    curated = curate_activity_records(records)
    assert curated == []

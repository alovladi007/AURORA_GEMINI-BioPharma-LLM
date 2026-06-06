"""
Unit tests for scaffold splitting.

Requires RDKit (installed via requirements.txt in CI).
"""

import pytest

pytest.importorskip("rdkit")

from app.ml.common.splits import scaffold_split


# A small but chemically diverse set of valid SMILES.
SMILES = [
    "CC(=O)OC1=CC=CC=C1C(=O)O",            # Aspirin
    "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",        # Ibuprofen
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",         # Caffeine
    "CC(C)NCC(COC1=CC=CC=C1)O",             # Propranolol
    "CN1CCC[C@H]1C1=CC=CN=C1",              # Nicotine
    "OC(=O)C1=CC=CC=C1O",                    # Salicylic acid
    "C1=CC=C(C=C1)C(=O)O",                   # Benzoic acid
    "CCO",                                    # Ethanol
    "CC(=O)NC1=CC=C(O)C=C1",                # Paracetamol
    "ClC1=CC=C(C=C1)C(Cl)Cl",               # an aryl chloride
]


def test_scaffold_split_partitions_all_indices():
    train, valid, test = scaffold_split(SMILES, frac_train=0.6, frac_valid=0.2)
    combined = sorted(train + valid + test)
    assert combined == list(range(len(SMILES)))


def test_scaffold_split_is_disjoint():
    train, valid, test = scaffold_split(SMILES, frac_train=0.6, frac_valid=0.2)
    assert set(train).isdisjoint(valid)
    assert set(train).isdisjoint(test)
    assert set(valid).isdisjoint(test)


def test_scaffold_split_is_deterministic():
    a = scaffold_split(SMILES, frac_train=0.6, frac_valid=0.2)
    b = scaffold_split(SMILES, frac_train=0.6, frac_valid=0.2)
    assert a == b


def test_scaffold_split_train_is_largest():
    train, valid, test = scaffold_split(SMILES, frac_train=0.6, frac_valid=0.2)
    assert len(train) >= len(test)

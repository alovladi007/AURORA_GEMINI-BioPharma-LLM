"""
Dataset splitting utilities for molecular ML.

Scaffold (Bemis–Murcko) splitting is the cheminformatics standard for honest
generalization estimates: molecules sharing a core scaffold are kept within the
same split so the test set measures performance on *novel* chemotypes rather
than near-duplicates of the training set.

RDKit is imported lazily.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


def _murcko_scaffold(smiles: str) -> Optional[str]:
    """Return the Bemis–Murcko scaffold SMILES, or None if invalid."""
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return Chem.MolToSmiles(scaffold, canonical=True)


def scaffold_split(
    smiles_list: Sequence[str],
    frac_train: float = 0.8,
    frac_valid: float = 0.1,
    seed: int = 42,
) -> Tuple[List[int], List[int], List[int]]:
    """
    Split indices into train/valid/test by Bemis–Murcko scaffold.

    Largest scaffold groups are assigned to train first (deterministic),
    so the test set contains the rarer, more novel scaffolds.

    Args:
        smiles_list: molecule SMILES.
        frac_train / frac_valid: fractions; test gets the remainder.
        seed: reserved for tie-breaking determinism.

    Returns:
        (train_idx, valid_idx, test_idx)
    """
    assert 0 < frac_train < 1 and 0 <= frac_valid < 1, "invalid fractions"
    assert frac_train + frac_valid < 1.0, "fractions must leave room for test"

    scaffolds: dict[str, List[int]] = defaultdict(list)
    n_invalid = 0
    for idx, smiles in enumerate(smiles_list):
        scaffold = _murcko_scaffold(smiles)
        if scaffold is None:
            # Invalid molecules form their own bucket so they don't pollute groups.
            scaffold = f"__invalid_{idx}__"
            n_invalid += 1
        scaffolds[scaffold].append(idx)

    # Sort scaffold sets: largest first (and by key for determinism).
    scaffold_sets = sorted(
        scaffolds.values(), key=lambda idxs: (len(idxs), idxs[0]), reverse=True
    )

    n_total = len(smiles_list)
    n_train_target = frac_train * n_total
    n_valid_target = frac_valid * n_total

    train_idx: List[int] = []
    valid_idx: List[int] = []
    test_idx: List[int] = []

    for group in scaffold_sets:
        if len(train_idx) + len(group) <= n_train_target:
            train_idx.extend(group)
        elif len(valid_idx) + len(group) <= n_valid_target:
            valid_idx.extend(group)
        else:
            test_idx.extend(group)

    logger.info(
        "Scaffold split: train=%d valid=%d test=%d (unique scaffolds=%d, invalid=%d)",
        len(train_idx), len(valid_idx), len(test_idx), len(scaffold_sets), n_invalid,
    )
    return train_idx, valid_idx, test_idx

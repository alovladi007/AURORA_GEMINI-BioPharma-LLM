"""
Common ML utilities for Pharma AI Platform.

Shared utilities for data validation, preprocessing, and helper functions.
"""

from typing import List, Optional, Tuple, Any
import numpy as np
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


def validate_smiles_list(smiles_list: List[str]) -> Tuple[List[str], List[int]]:
    """
    Validate a list of SMILES strings.

    Args:
        smiles_list: List of SMILES strings

    Returns:
        Tuple of (valid_smiles, invalid_indices)
    """
    try:
        from rdkit import Chem
    except ImportError:
        logger.error("RDKit not installed. Cannot validate SMILES.")
        return smiles_list, []

    valid_smiles = []
    invalid_indices = []

    for i, smiles in enumerate(smiles_list):
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            invalid_indices.append(i)
            logger.warning(f"Invalid SMILES at index {i}: {smiles}")
        else:
            valid_smiles.append(smiles)

    return valid_smiles, invalid_indices


def split_dataset(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split dataset into train and test sets.

    Args:
        X: Feature matrix
        y: Target vector
        test_size: Fraction for test set
        random_state: Random seed
        stratify: Array for stratified split

    Returns:
        X_train, X_test, y_train, y_test
    """
    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify
    )


def normalize_array(arr: np.ndarray, method: str = "standard") -> Tuple[np.ndarray, dict]:
    """
    Normalize array using specified method.

    Args:
        arr: Input array
        method: Normalization method ("standard", "minmax", "robust")

    Returns:
        Tuple of (normalized_array, normalization_params)
    """
    if method == "standard":
        mean = np.mean(arr, axis=0)
        std = np.std(arr, axis=0)
        normalized = (arr - mean) / (std + 1e-8)
        params = {"method": "standard", "mean": mean.tolist(), "std": std.tolist()}

    elif method == "minmax":
        min_val = np.min(arr, axis=0)
        max_val = np.max(arr, axis=0)
        normalized = (arr - min_val) / (max_val - min_val + 1e-8)
        params = {"method": "minmax", "min": min_val.tolist(), "max": max_val.tolist()}

    elif method == "robust":
        median = np.median(arr, axis=0)
        q75 = np.percentile(arr, 75, axis=0)
        q25 = np.percentile(arr, 25, axis=0)
        iqr = q75 - q25
        normalized = (arr - median) / (iqr + 1e-8)
        params = {"method": "robust", "median": median.tolist(), "iqr": iqr.tolist()}

    else:
        raise ValueError(f"Unknown normalization method: {method}")

    return normalized, params


def apply_normalization(arr: np.ndarray, params: dict) -> np.ndarray:
    """
    Apply normalization using saved parameters.

    Args:
        arr: Input array
        params: Normalization parameters from normalize_array

    Returns:
        Normalized array
    """
    method = params["method"]

    if method == "standard":
        mean = np.array(params["mean"])
        std = np.array(params["std"])
        return (arr - mean) / (std + 1e-8)

    elif method == "minmax":
        min_val = np.array(params["min"])
        max_val = np.array(params["max"])
        return (arr - min_val) / (max_val - min_val + 1e-8)

    elif method == "robust":
        median = np.array(params["median"])
        iqr = np.array(params["iqr"])
        return (arr - median) / (iqr + 1e-8)

    else:
        raise ValueError(f"Unknown normalization method: {method}")


def pad_or_truncate(arr: np.ndarray, target_length: int, pad_value: float = 0.0) -> np.ndarray:
    """
    Pad or truncate array to target length.

    Args:
        arr: Input array
        target_length: Target length
        pad_value: Value to use for padding

    Returns:
        Padded or truncated array
    """
    current_length = len(arr)

    if current_length == target_length:
        return arr
    elif current_length < target_length:
        # Pad
        padding = np.full(target_length - current_length, pad_value)
        return np.concatenate([arr, padding])
    else:
        # Truncate
        return arr[:target_length]


def compute_class_weights(y: np.ndarray) -> dict:
    """
    Compute class weights for imbalanced datasets.

    Args:
        y: Target labels

    Returns:
        Dictionary mapping class to weight
    """
    unique, counts = np.unique(y, return_counts=True)
    total = len(y)
    weights = {
        int(cls): total / (len(unique) * count)
        for cls, count in zip(unique, counts)
    }
    return weights


def ensure_numpy(data: Any) -> np.ndarray:
    """
    Ensure data is numpy array.

    Args:
        data: Input data (list, array, tensor, etc.)

    Returns:
        Numpy array
    """
    if isinstance(data, np.ndarray):
        return data
    elif isinstance(data, list):
        return np.array(data)
    else:
        # Try to convert (handles torch tensors, etc.)
        try:
            return np.array(data)
        except:
            raise TypeError(f"Cannot convert {type(data)} to numpy array")


def batch_iterator(data: List[Any], batch_size: int):
    """
    Iterate over data in batches.

    Args:
        data: List of data items
        batch_size: Batch size

    Yields:
        Batches of data
    """
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

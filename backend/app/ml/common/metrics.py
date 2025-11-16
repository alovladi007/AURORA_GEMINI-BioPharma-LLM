"""
ML evaluation metrics for Pharma AI Platform.

Common metrics for classification, regression, and ranking tasks.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
import logging

logger = logging.getLogger(__name__)


def classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    average: str = "binary"
) -> Dict[str, float]:
    """
    Compute classification metrics.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Predicted probabilities (for AUC)
        average: Averaging method for multiclass ("binary", "macro", "micro", "weighted")

    Returns:
        Dictionary of metrics
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average=average, zero_division=0),
        "recall": recall_score(y_true, y_pred, average=average, zero_division=0),
        "f1": f1_score(y_true, y_pred, average=average, zero_division=0),
    }

    # Add AUC metrics if probabilities provided
    if y_prob is not None:
        try:
            if average == "binary":
                metrics["auroc"] = roc_auc_score(y_true, y_prob)
                metrics["auprc"] = average_precision_score(y_true, y_prob)
            else:
                # Multiclass
                metrics["auroc"] = roc_auc_score(y_true, y_prob, average=average, multi_class="ovr")
        except ValueError as e:
            logger.warning(f"Could not compute AUC: {e}")

    return metrics


def regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Compute regression metrics.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        Dictionary of metrics
    """
    mse = mean_squared_error(y_true, y_pred)

    metrics = {
        "mse": mse,
        "rmse": np.sqrt(mse),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }

    # Compute Pearson correlation
    if len(y_true) > 1:
        correlation_matrix = np.corrcoef(y_true, y_pred)
        metrics["pearson_r"] = correlation_matrix[0, 1]

    return metrics


def enrichment_factor(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    fraction: float = 0.01
) -> float:
    """
    Compute enrichment factor for drug discovery.

    Measures how many times more actives are found in top-ranked
    compounds compared to random selection.

    Args:
        y_true: True binary labels (1 = active, 0 = inactive)
        y_scores: Predicted scores (higher = more likely active)
        fraction: Fraction of top compounds to consider (default: 1%)

    Returns:
        Enrichment factor
    """
    n = len(y_true)
    n_top = max(1, int(n * fraction))
    n_actives = np.sum(y_true)

    if n_actives == 0:
        return 0.0

    # Get indices of top-ranked compounds
    top_indices = np.argsort(y_scores)[-n_top:]

    # Count actives in top-ranked
    actives_in_top = np.sum(y_true[top_indices])

    # Expected actives if random
    expected_actives = n_actives * fraction

    # Enrichment factor
    ef = actives_in_top / expected_actives if expected_actives > 0 else 0.0

    return ef


def bedroc_score(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    alpha: float = 20.0
) -> float:
    """
    Compute BEDROC (Boltzmann-Enhanced Discrimination of ROC).

    A metric commonly used in drug discovery that emphasizes early recognition.

    Args:
        y_true: True binary labels
        y_scores: Predicted scores
        alpha: Early recognition parameter (default: 20.0)

    Returns:
        BEDROC score (0-1, higher is better)
    """
    # Sort by scores (descending)
    order = np.argsort(y_scores)[::-1]
    y_sorted = y_true[order]

    n = len(y_true)
    n_actives = np.sum(y_true)

    if n_actives == 0 or n_actives == n:
        return 0.0

    # Compute BEDROC
    ri = np.where(y_sorted == 1)[0] + 1  # Ranks of actives (1-indexed)
    s = np.sum(np.exp(-alpha * ri / n))

    r_max = (1.0 - np.exp(-alpha)) / (np.exp(alpha / n) - 1.0)
    r_min = n_actives * (1.0 - np.exp(-alpha / n)) / (1.0 - np.exp(-alpha))

    bedroc = (s - r_min) / (r_max - r_min)

    return max(0.0, min(1.0, bedroc))


def compute_confusion_matrix_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, int]:
    """
    Compute confusion matrix components.

    Args:
        y_true: True binary labels
        y_pred: Predicted binary labels

    Returns:
        Dictionary with TP, TN, FP, FN, sensitivity, specificity
    """
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    return {
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
    }


def top_k_accuracy(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    k: int = 10
) -> float:
    """
    Compute top-K accuracy.

    Measures whether true label is in top K predictions.

    Args:
        y_true: True labels
        y_scores: Prediction scores (n_samples, n_classes)
        k: Number of top predictions to consider

    Returns:
        Top-K accuracy (0-1)
    """
    if y_scores.ndim == 1:
        # Binary case - just use threshold
        top_k_pred = (y_scores >= np.sort(y_scores)[-k]) if k < len(y_scores) else np.ones_like(y_scores)
        return np.mean(y_true == top_k_pred)

    # Multiclass case
    top_k_indices = np.argsort(y_scores, axis=1)[:, -k:]
    correct = 0

    for i, true_label in enumerate(y_true):
        if true_label in top_k_indices[i]:
            correct += 1

    return correct / len(y_true)


def calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> Tuple[float, List[float], List[float]]:
    """
    Compute expected calibration error (ECE).

    Measures how well predicted probabilities match actual frequencies.

    Args:
        y_true: True binary labels
        y_prob: Predicted probabilities
        n_bins: Number of bins for calibration curve

    Returns:
        Tuple of (ece, bin_accuracies, bin_confidences)
    """
    bins = np.linspace(0, 1, n_bins + 1)
    bin_accuracies = []
    bin_confidences = []
    ece = 0.0

    for i in range(n_bins):
        # Get samples in this bin
        mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
        if i == n_bins - 1:  # Include upper bound in last bin
            mask = (y_prob >= bins[i]) & (y_prob <= bins[i + 1])

        if np.sum(mask) > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            bin_size = np.sum(mask)

            bin_accuracies.append(bin_acc)
            bin_confidences.append(bin_conf)

            # Add to ECE
            ece += (bin_size / len(y_true)) * np.abs(bin_acc - bin_conf)
        else:
            bin_accuracies.append(0.0)
            bin_confidences.append(bins[i])

    return ece, bin_accuracies, bin_confidences

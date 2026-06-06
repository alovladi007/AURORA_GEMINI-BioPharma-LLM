"""
Lightweight model registry helpers.

Persists model artifacts alongside a JSON sidecar (metrics, provenance,
hyperparameters) and renders a human-readable Markdown model card. This is the
local-filesystem implementation; Phase 5 swaps the backend for MLflow + S3
without changing call sites.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def artifacts_dir() -> str:
    """Resolve the configured artifacts directory, creating it if needed."""
    path = settings.MODEL_ARTIFACTS_PATH
    os.makedirs(path, exist_ok=True)
    return path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_metadata(
    model_name: str,
    metadata: Dict[str, Any],
    directory: Optional[str] = None,
) -> str:
    """Write a `<model_name>.metadata.json` sidecar. Returns the path."""
    directory = directory or artifacts_dir()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{model_name}.metadata.json")
    payload = {"created_at": _now_iso(), **metadata}
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2, default=str)
    logger.info("Wrote model metadata to %s", path)
    return path


def render_model_card(
    model_name: str,
    *,
    task: str,
    description: str,
    data_source: str,
    n_train: int,
    n_valid: int,
    n_test: int,
    split_strategy: str,
    featurization: str,
    algorithm: str,
    hyperparameters: Dict[str, Any],
    metrics: Dict[str, Any],
    limitations: str = "",
    output_dir: Optional[str] = None,
) -> str:
    """Render a Markdown model card to `ml/model_cards/<model_name>.md`."""
    output_dir = output_dir or os.path.join(os.getcwd(), "ml", "model_cards")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{model_name}.md")

    def _metrics_table(m: Dict[str, Any]) -> str:
        rows = []
        for key, value in m.items():
            if isinstance(value, (int, float)):
                rows.append(f"| {key} | {value:.4f} |")
            elif isinstance(value, str):
                rows.append(f"| {key} | {value} |")
        return "\n".join(rows) if rows else "| (none) | - |"

    card = f"""# Model Card — `{model_name}`

> ⚕️ **Research use only.** Predictions are computational hypotheses and must be
> validated experimentally. Not for clinical or diagnostic use.

## Overview
- **Task:** {task}
- **Description:** {description}
- **Algorithm:** {algorithm}
- **Featurization:** {featurization}
- **Created:** {_now_iso()}

## Data
- **Source:** {data_source}
- **Split strategy:** {split_strategy}
- **Sizes:** train={n_train}, valid={n_valid}, test={n_test}

## Hyperparameters
```json
{json.dumps(hyperparameters, indent=2, default=str)}
```

## Evaluation (held-out test set)
| Metric | Value |
|--------|-------|
{_metrics_table(metrics)}

## Limitations
{limitations or "Performance is bounded by the coverage and quality of the training data. "
 "Predictions on chemotypes far from the training distribution are unreliable."}
"""
    with open(path, "w") as fh:
        fh.write(card)
    logger.info("Wrote model card to %s", path)
    return path

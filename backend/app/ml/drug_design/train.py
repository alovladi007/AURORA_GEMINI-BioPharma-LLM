"""
Real SAR (Structure–Activity Relationship) model training pipeline.

Runnable as:  python -m app.ml.drug_design.train --input <curated.csv>
Importable as: from app.ml.drug_design.train import train_sar

Pipeline:
  1. Load curated data (columns: smiles, label[, pchembl_value]) — or ingest a
     ChEMBL target on the fly with target=...
  2. Featurize with Morgan fingerprints (r=2, 2048 bits) — identical to inference.
  3. Bemis–Murcko scaffold split (honest generalization estimate).
  4. Train a RandomForest SAR predictor (the same class used at inference).
  5. Evaluate on the held-out test set (scaffold split).
  6. Save the artifact (loadable by SARInference), metadata sidecar, and model card.

Heavy deps (rdkit/sklearn/numpy/pandas) are imported inside functions so the
module can be imported for discovery without them present.
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# A no-op progress callback signature: fn(percent: int, message: str) -> None
ProgressFn = Callable[[int, str], None]


def _noop_progress(percent: int, message: str) -> None:  # pragma: no cover - trivial
    logger.info("[%3d%%] %s", percent, message)


def _load_csv(path: str) -> Tuple[List[str], List[int]]:
    """Load a curated CSV with at least `smiles` and `label` columns."""
    smiles: List[str] = []
    labels: List[int] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or "smiles" not in reader.fieldnames:
            raise ValueError("CSV must have a 'smiles' column")
        if "label" not in reader.fieldnames:
            raise ValueError("CSV must have a 'label' column for classification")
        for row in reader:
            smiles.append(row["smiles"])
            labels.append(int(float(row["label"])))
    logger.info("Loaded %d rows from %s", len(smiles), path)
    return smiles, labels


def _ingest_chembl_to_csv(target: str, output_csv: str, max_records: Optional[int]) -> str:
    """Pull a ChEMBL target, curate, and write a CSV. Returns the CSV path."""
    from app.data.chembl_client import ChEMBLClient
    from app.data.curation import curate_activity_records, write_dataset_csv

    client = ChEMBLClient()
    raw = client.fetch_activities(target, max_records=max_records)
    curated = curate_activity_records(raw)
    if not curated:
        raise RuntimeError(f"No curated molecules produced for target {target}")
    write_dataset_csv(curated, output_csv)
    return output_csv


def train_sar(
    input_csv: Optional[str] = None,
    target: Optional[str] = None,
    max_records: Optional[int] = None,
    model_name: str = "sar_random_forest",
    fp_bits: int = 2048,
    fp_radius: int = 2,
    n_estimators: int = 300,
    max_depth: int = 20,
    seed: int = 42,
    progress: Optional[ProgressFn] = None,
) -> Dict:
    """
    Train a real SAR classifier end-to-end and persist artifact + model card.

    Returns a JSON-serializable result dict:
        {
          model_name, artifact_path, metadata_path, model_card_path,
          data_source, n_train, n_valid, n_test, hyperparameters, test_metrics
        }
    """
    progress = progress or _noop_progress

    # Heavy imports (kept local so module import never requires them)
    import numpy as np
    from app.ml.common.featurization import MolecularFeaturizer
    from app.ml.common.splits import scaffold_split
    from app.ml.common.metrics import classification_metrics
    from app.ml.common.registry import artifacts_dir, write_metadata, render_model_card
    from app.ml.drug_design.models import RandomForestSARPredictor

    # 1. Resolve dataset ------------------------------------------------------
    progress(5, "Resolving dataset")
    data_source = f"CSV: {input_csv}"
    if not input_csv:
        if not target:
            raise ValueError("Provide either input_csv or target")
        os.makedirs("ml/data/processed", exist_ok=True)
        input_csv = f"ml/data/processed/{target}_curated.csv"
        progress(10, f"Ingesting ChEMBL target {target}")
        _ingest_chembl_to_csv(target, input_csv, max_records)
        data_source = f"ChEMBL target {target}"

    smiles, labels = _load_csv(input_csv)
    if len(set(labels)) < 2:
        raise RuntimeError("Dataset has a single class; cannot train a classifier")

    # 2. Featurize ------------------------------------------------------------
    progress(30, f"Featurizing {len(smiles)} molecules (Morgan r{fp_radius}, {fp_bits}b)")
    X = MolecularFeaturizer.batch_featurize(
        smiles, method="morgan", radius=fp_radius, n_bits=fp_bits
    )
    y = np.array(labels)

    # 3. Scaffold split -------------------------------------------------------
    progress(45, "Scaffold splitting")
    train_idx, valid_idx, test_idx = scaffold_split(smiles, seed=seed)
    fit_idx = train_idx + valid_idx  # fold valid into the final fit
    X_train, y_train = X[fit_idx], y[fit_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    if len(X_test) == 0:
        raise RuntimeError("Empty test split; need a larger / more diverse dataset")

    # 4. Train ----------------------------------------------------------------
    progress(60, f"Training RandomForest on {len(X_train)} molecules")
    model = RandomForestSARPredictor(
        task="classification",
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=seed,
    )
    model.fit(X_train, y_train)

    # 5. Evaluate on held-out scaffold test set -------------------------------
    progress(80, "Evaluating on held-out test set")
    test_preds = model.predict(X_test)
    test_proba = model.predict_proba(X_test)[:, 1]
    test_metrics = classification_metrics(y_test, test_preds, test_proba)
    test_metrics = {k: v for k, v in test_metrics.items() if isinstance(v, (int, float, str))}
    logger.info(
        "TEST  acc=%.3f  auroc=%.3f  f1=%.3f",
        test_metrics.get("accuracy", float("nan")),
        test_metrics.get("auroc", float("nan")),
        test_metrics.get("f1", float("nan")),
    )

    # 6. Persist artifact + metadata + model card -----------------------------
    progress(90, "Persisting artifact and model card")
    out_dir = artifacts_dir()
    artifact_path = os.path.join(out_dir, f"{model_name}.joblib")
    model.save(artifact_path)
    logger.info("Saved model artifact → %s", artifact_path)

    hyperparameters = {
        "algorithm": "RandomForestClassifier",
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "featurization": f"morgan_r{fp_radius}_{fp_bits}bit",
        "seed": seed,
    }
    metadata_path = write_metadata(
        model_name,
        {
            "artifact_path": artifact_path,
            "task": "classification",
            "data_source": data_source,
            "n_train": len(train_idx),
            "n_valid": len(valid_idx),
            "n_test": len(test_idx),
            "hyperparameters": hyperparameters,
            "test_metrics": test_metrics,
        },
    )
    model_card_path = render_model_card(
        model_name,
        task="classification (active vs. inactive, pChEMBL ≥ 6.0)",
        description="Structure–Activity Relationship classifier predicting whether a "
        "molecule is active against the target.",
        data_source=data_source,
        n_train=len(train_idx),
        n_valid=len(valid_idx),
        n_test=len(test_idx),
        split_strategy="Bemis–Murcko scaffold split (80/10/10)",
        featurization=f"Morgan fingerprint r={fp_radius}, {fp_bits} bits",
        algorithm="RandomForestClassifier",
        hyperparameters=hyperparameters,
        metrics=test_metrics,
    )

    # Optional MLflow tracking (no-op unless MLFLOW_TRACKING_URI is set).
    from app.ml.common.tracking import mlflow_run, log_params, log_metrics, log_artifact

    with mlflow_run(run_name=model_name, tags={"module": "drug_design", "task": "sar"}):
        log_params({**hyperparameters, "data_source": data_source,
                    "n_train": len(train_idx), "n_test": len(test_idx)})
        log_metrics(test_metrics)
        log_artifact(metadata_path)
        log_artifact(model_card_path)

    progress(100, "Training complete")
    return {
        "model_name": model_name,
        "artifact_path": artifact_path,
        "metadata_path": metadata_path,
        "model_card_path": model_card_path,
        "data_source": data_source,
        "n_train": len(train_idx),
        "n_valid": len(valid_idx),
        "n_test": len(test_idx),
        "hyperparameters": hyperparameters,
        "test_metrics": test_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a real SAR model")
    parser.add_argument("--input", help="Curated CSV (smiles,label[,pchembl_value])")
    parser.add_argument("--target", help="ChEMBL target id to ingest if --input absent")
    parser.add_argument("--max-records", type=int, default=None, help="Cap ChEMBL records")
    parser.add_argument("--model-name", default="sar_random_forest")
    parser.add_argument("--fp-bits", type=int, default=2048)
    parser.add_argument("--fp-radius", type=int, default=2)
    parser.add_argument("--n-estimators", type=int, default=300)
    parser.add_argument("--max-depth", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if not args.input and not args.target:
        parser.error("Provide either --input <csv> or --target <CHEMBL_ID>")

    result = train_sar(
        input_csv=args.input,
        target=args.target,
        max_records=args.max_records,
        model_name=args.model_name,
        fp_bits=args.fp_bits,
        fp_radius=args.fp_radius,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        seed=args.seed,
    )
    logger.info("✓ Training complete for '%s' — test metrics: %s",
                result["model_name"], result["test_metrics"])


if __name__ == "__main__":
    main()

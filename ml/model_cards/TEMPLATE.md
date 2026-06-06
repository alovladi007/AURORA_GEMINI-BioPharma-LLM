# Model Card — `<model_name>`

> ⚕️ **Research use only.** Predictions are computational hypotheses and must be
> validated experimentally. Not for clinical or diagnostic use.

## Overview
- **Task:** <classification | regression | generation | ranking>
- **Description:** <what the model predicts and why>
- **Algorithm:** <e.g., Random Forest, GBT, MLP, SMILES-Transformer, R-GCN>
- **Featurization:** <e.g., Morgan r2 2048-bit, RDKit descriptors, graph>
- **Version:** <semver>
- **Created:** <ISO timestamp>

## Intended Use
- **Primary users:** <medicinal chemists, comp-chem, biostatisticians>
- **In scope:** <decision support, triage, hypothesis generation>
- **Out of scope:** clinical decisions, regulatory submissions, wet-lab protocols.

## Data
- **Source:** <ChEMBL target id / TDC dataset / Open Targets / etc.>
- **Provenance & license:** <link + license>
- **Curation:** <standardization, dedup, unit handling, label definition>
- **Split strategy:** <scaffold split (preferred) | random | temporal>
- **Sizes:** train=<n>, valid=<n>, test=<n>
- **Class balance:** <active/inactive counts>

## Hyperparameters
```json
{ }
```

## Evaluation (held-out test set)
| Metric | Value |
|--------|-------|
| <auc_roc / rmse / ...> | <value> |

Include calibration (for classifiers), confusion matrix, and a comparison to a
published baseline where available.

## Limitations & Risks
- Distribution shift: unreliable outside training chemotypes.
- Label noise / assay variability.
- Known failure modes: <...>

## Maintenance
- **Owner:** <team>
- **Retraining trigger:** <drift threshold / schedule>
- **Changelog:** <versions>

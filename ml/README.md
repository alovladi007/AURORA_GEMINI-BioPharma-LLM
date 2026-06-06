# ML Pipeline — Data → Train → Serve

This directory holds datasets, model artifacts, and model cards. As of Phase 1,
the **Drug Design SAR** module has a complete, real (non-demo) pipeline.

## Layout
```
ml/
├── data/
│   ├── raw/            # raw pulls (gitignored content)
│   └── processed/      # curated, model-ready CSVs
├── models/
│   └── artifacts/      # trained model artifacts (.joblib) + metadata sidecars
└── model_cards/        # human-readable model cards (TEMPLATE.md + generated)
```

## End-to-end: train a real SAR model from ChEMBL

```bash
# 1. Ingest a target's bioactivities and curate to a labeled CSV
#    (EGFR = CHEMBL203). Produces ml/data/processed/CHEMBL203_curated.csv
python -m app.data.ingest chembl --target CHEMBL203

# 2. Train a scaffold-split RandomForest SAR classifier.
#    Produces:
#      - ml/models/artifacts/sar_random_forest.joblib   (loadable by the API)
#      - ml/models/artifacts/sar_random_forest.metadata.json
#      - ml/model_cards/sar_random_forest.md
python -m app.ml.drug_design.train \
    --input ml/data/processed/CHEMBL203_curated.csv \
    --model-name sar_random_forest

# (or do both at once)
python -m app.ml.drug_design.train --target CHEMBL203
```

The API (`POST /api/v1/drug-design/predict-sar`) automatically prefers
`sar_random_forest.joblib` once it exists, falling back to a demo model only if
no trained artifact is present.

## Why scaffold splits?
Random splits leak near-duplicate analogs between train and test and inflate
metrics. We use **Bemis–Murcko scaffold splits** so the test set measures
generalization to genuinely novel chemotypes — the number that matters for
prospective drug discovery.

## What's real vs. still demo (Phase 1)
| Module | Status |
|--------|--------|
| Drug Design — SAR | ✅ Real: ChEMBL ingestion → scaffold split → RF → model card |
| Drug Design — generation/optimization | ⏳ Demo (Phase 2: generative models) |
| Safety / Clinical / Repurposing | ⏳ Demo (Phases 2–4) |

See `../ROADMAP.md` for the full 18-month plan.

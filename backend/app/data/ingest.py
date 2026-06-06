"""
Data ingestion CLI.

Examples:
    # Pull EGFR (CHEMBL203) bioactivities and write a curated CSV
    python -m app.data.ingest chembl --target CHEMBL203 \
        --output ml/data/processed/CHEMBL203_curated.csv

The curated CSV (smiles,pchembl_value,label) feeds the SAR trainer:
    python -m app.ml.drug_design.train --input ml/data/processed/CHEMBL203_curated.csv
"""

from __future__ import annotations

import argparse
import logging
import sys


def _run_chembl(args: argparse.Namespace) -> int:
    from app.data.chembl_client import ChEMBLClient
    from app.data.curation import curate_activity_records, write_dataset_csv

    client = ChEMBLClient()
    records = client.fetch_activities(args.target, max_records=args.max_records)
    if not records:
        logging.error("No activity records returned for %s", args.target)
        return 1

    curated = curate_activity_records(records, pchembl_threshold=args.threshold)
    if not curated:
        logging.error("Curation produced 0 usable molecules for %s", args.target)
        return 1

    output = args.output or f"ml/data/processed/{args.target}_curated.csv"
    write_dataset_csv(curated, output)
    n_active = sum(r["label"] for r in curated)
    logging.info(
        "Done: %d molecules (%d active / %d inactive) → %s",
        len(curated), n_active, len(curated) - n_active, output,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BioPharma data ingestion")
    sub = parser.add_subparsers(dest="source", required=True)

    chembl = sub.add_parser("chembl", help="Ingest bioactivities from ChEMBL")
    chembl.add_argument("--target", required=True, help="ChEMBL target id, e.g. CHEMBL203")
    chembl.add_argument("--output", help="Output CSV path")
    chembl.add_argument("--max-records", type=int, default=None, help="Cap records (for testing)")
    chembl.add_argument("--threshold", type=float, default=6.0, help="pChEMBL active threshold")
    chembl.set_defaults(func=_run_chembl)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

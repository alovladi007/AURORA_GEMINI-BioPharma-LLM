"""
ChEMBL REST API client.

Pulls real bioactivity measurements for a given target and returns a tidy
list of (SMILES, standard_value, standard_units, pchembl_value) records.

Docs: https://www.ebi.ac.uk/chembl/api/data/docs

Network access is required at runtime. The client paginates, retries with
exponential backoff, and is conservative with request rate to respect the API.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Iterator, List, Optional

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"


class ChEMBLClient:
    """Minimal, dependency-light ChEMBL client built on httpx."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 4,
        page_size: int = 1000,
        request_delay: float = 0.2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.page_size = page_size
        self.request_delay = request_delay

    # ------------------------------------------------------------------ #
    # Low-level HTTP
    # ------------------------------------------------------------------ #
    def _get(self, path: str, params: Dict) -> Dict:
        """GET with retry/backoff. `path` is relative to base_url."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_err: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.get(url, params=params)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.HTTPError, ValueError) as exc:  # ValueError = bad JSON
                last_err = exc
                backoff = 2 ** attempt
                logger.warning(
                    "ChEMBL request failed (attempt %d/%d): %s — retrying in %ds",
                    attempt + 1, self.max_retries, exc, backoff,
                )
                time.sleep(backoff)

        raise RuntimeError(f"ChEMBL request failed after {self.max_retries} attempts: {last_err}")

    def _paginate(self, path: str, params: Dict, collection_key: str) -> Iterator[Dict]:
        """Yield every record across all pages for a list endpoint."""
        params = dict(params)
        params.setdefault("limit", self.page_size)
        params.setdefault("offset", 0)

        while True:
            payload = self._get(path, params)
            records = payload.get(collection_key, [])
            for rec in records:
                yield rec

            page_meta = payload.get("page_meta", {})
            next_url = page_meta.get("next")
            if not next_url or not records:
                break

            params["offset"] = params["offset"] + params["limit"]
            time.sleep(self.request_delay)

    # ------------------------------------------------------------------ #
    # High-level
    # ------------------------------------------------------------------ #
    def fetch_activities(
        self,
        target_chembl_id: str,
        standard_types: Optional[List[str]] = None,
        max_records: Optional[int] = None,
    ) -> List[Dict]:
        """
        Fetch bioactivity records for a target.

        Args:
            target_chembl_id: e.g. "CHEMBL203" (EGFR)
            standard_types: activity types to keep (default: IC50/Ki/Kd/EC50)
            max_records: optional cap for quick experiments

        Returns:
            List of dicts with keys:
            canonical_smiles, standard_type, standard_value, standard_units,
            pchembl_value, molecule_chembl_id
        """
        standard_types = standard_types or ["IC50", "Ki", "Kd", "EC50"]
        params = {
            "target_chembl_id": target_chembl_id,
            "standard_type__in": ",".join(standard_types),
            "format": "json",
        }

        results: List[Dict] = []
        for rec in self._paginate("activity.json", params, "activities"):
            smiles = rec.get("canonical_smiles")
            if not smiles:
                continue
            results.append(
                {
                    "molecule_chembl_id": rec.get("molecule_chembl_id"),
                    "canonical_smiles": smiles,
                    "standard_type": rec.get("standard_type"),
                    "standard_value": rec.get("standard_value"),
                    "standard_units": rec.get("standard_units"),
                    "pchembl_value": rec.get("pchembl_value"),
                }
            )
            if max_records is not None and len(results) >= max_records:
                break

        logger.info(
            "Fetched %d activity records for target %s", len(results), target_chembl_id
        )
        return results

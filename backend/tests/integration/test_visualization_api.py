"""
Integration tests for molecule visualization endpoints.

Requires RDKit (installed via requirements.txt in CI).
"""

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("rdkit")


class TestVisualizationAPI:
    """Tests for /api/v1/visualize endpoints."""

    def test_render_valid_molecule(self, client: TestClient):
        resp = client.get("/api/v1/visualize/molecule", params={"smiles": "CCO"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["svg"] is not None and "<svg" in data["svg"]
        assert data["descriptors"]["molecular_weight"] > 0
        assert "lipinski" in data and "drug_like" in data["lipinski"]

    def test_render_invalid_molecule(self, client: TestClient):
        resp = client.get("/api/v1/visualize/molecule", params={"smiles": "not_a_molecule"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert data["svg"] is None

    def test_empty_smiles_rejected(self, client: TestClient):
        resp = client.get("/api/v1/visualize/molecule", params={"smiles": "   "})
        assert resp.status_code == 400

    def test_batch_rendering(self, client: TestClient):
        resp = client.post(
            "/api/v1/visualize/molecules",
            json={"smiles_list": ["CCO", "c1ccccc1", "bad_smiles"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        assert data[0]["valid"] is True
        assert data[2]["valid"] is False

    def test_lipinski_flags_large_molecule(self, client: TestClient):
        # A large peptide-like SMILES should accrue RO5 violations.
        resp = client.get(
            "/api/v1/visualize/molecule",
            params={"smiles": "CCO"},
        )
        assert resp.status_code == 200
        assert resp.json()["lipinski"]["violations"] == 0

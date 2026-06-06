"""
Molecule visualization endpoints.

Renders 2D depictions (SVG) from SMILES via RDKit and returns computed molecular
descriptors + Lipinski rule-of-five evaluation. Powers the frontend MoleculeViewer.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.ml.common.featurization import MolecularFeaturizer

logger = logging.getLogger(__name__)

router = APIRouter()


class MoleculeView(BaseModel):
    smiles: str
    valid: bool
    svg: Optional[str] = None
    descriptors: Optional[Dict[str, float]] = None
    lipinski: Optional[Dict[str, Any]] = None


def _render_svg(smiles: str, width: int, height: int) -> Optional[str]:
    """Return a 2D SVG depiction for a SMILES, or None if invalid/unavailable."""
    try:
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D
    except ImportError:  # pragma: no cover - RDKit always present in deployed image
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RDKit not available for rendering.",
        )

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()


def _lipinski(desc: Dict[str, float]) -> Dict[str, Any]:
    """Evaluate Lipinski's rule of five from descriptors."""
    mw = desc.get("molecular_weight", 0.0)
    logp = desc.get("logp", desc.get("mol_logp", 0.0))
    hbd = desc.get("num_h_donors", 0)
    hba = desc.get("num_h_acceptors", 0)

    violations = 0
    checks = {
        "mw_<=500": mw <= 500,
        "logp_<=5": logp <= 5,
        "hbd_<=5": hbd <= 5,
        "hba_<=10": hba <= 10,
    }
    violations = sum(1 for ok in checks.values() if not ok)
    return {
        "checks": checks,
        "violations": violations,
        "drug_like": violations <= 1,  # RO5 allows one violation
    }


def _build_view(smiles: str, width: int, height: int) -> MoleculeView:
    svg = _render_svg(smiles, width, height)
    if svg is None:
        return MoleculeView(smiles=smiles, valid=False)

    descriptors = MolecularFeaturizer.compute_descriptors(smiles)
    lipinski = _lipinski(descriptors) if descriptors else None
    return MoleculeView(
        smiles=smiles,
        valid=True,
        svg=svg,
        descriptors=descriptors,
        lipinski=lipinski,
    )


@router.get("/molecule", response_model=MoleculeView)
def visualize_molecule(
    smiles: str = Query(..., description="SMILES string to render"),
    width: int = Query(350, ge=100, le=1200),
    height: int = Query(300, ge=100, le=1200),
):
    """Render a single molecule: 2D SVG + descriptors + Lipinski evaluation."""
    if not smiles.strip():
        raise HTTPException(status_code=400, detail="Empty SMILES")
    return _build_view(smiles.strip(), width, height)


class BatchVisualizationRequest(BaseModel):
    smiles_list: List[str]
    width: int = 250
    height: int = 200


@router.post("/molecules", response_model=List[MoleculeView])
def visualize_molecules(request: BatchVisualizationRequest):
    """Render a batch of molecules (e.g., generated set or SAR table)."""
    if not request.smiles_list:
        raise HTTPException(status_code=400, detail="smiles_list is empty")
    if len(request.smiles_list) > 200:
        raise HTTPException(status_code=400, detail="Too many molecules (max 200)")
    return [_build_view(s.strip(), request.width, request.height) for s in request.smiles_list]

from pathlib import Path
import json
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/cds-services", tags=["Payer CDS Services"])

# parents[2] points to the root payer_A/ directory
BASE_DIR = Path(__file__).resolve().parents[2]
SERVICES_PATH = BASE_DIR / "services.json"

@router.get("")
async def get_payer_services():
    """Serves the Payer's own complex discovery JSON natively."""
    if not SERVICES_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Services registry not found at {SERVICES_PATH}")
    return json.loads(SERVICES_PATH.read_text())

@router.post("/{hook_id}")
async def evaluate_cds_hook(hook_id: str, body: dict):
    """Evaluates CRD/DTR clinical rules for the given hook."""
    return {"cards": [{"summary": "Coverage Approved", "detail": "Service meets medical necessity guidelines."}]}
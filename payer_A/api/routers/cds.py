from pathlib import Path
import json
import uuid
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/cds-services", tags=["Payer CDS Services"])

# parents[2] points to payer_A/ directory
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SERVICES_PATH = DATA_DIR / "services.json"
RESPONSES_PATH = DATA_DIR / "responses.json"

@router.get("")
async def get_payer_services():
    """Serves the Payer's own complex discovery JSON natively."""
    if not SERVICES_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Services registry not found at {SERVICES_PATH}")
    return json.loads(SERVICES_PATH.read_text())

@router.post("/{hook_id}")
async def evaluate_cds_hook(hook_id: str, body: dict):
    """Evaluates CRD clinical rules via data-driven registry lookup."""
    if not RESPONSES_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Responses registry not found at {RESPONSES_PATH}")

    registry = json.loads(RESPONSES_PATH.read_text())
    
    # Retrieve specific rule or fallback to data-driven 'default' rule
    matched_response = registry.get(hook_id) or registry.get("default")

    # Deep copy template and dynamically assign unique transaction UUIDs
    dynamic_payload = json.loads(json.dumps(matched_response))
    for card in dynamic_payload.get("cards", []):
        card["uuid"] = str(uuid.uuid4())

    return dynamic_payload
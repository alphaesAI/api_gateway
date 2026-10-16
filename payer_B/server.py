from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from payer_B.engine import MalformedRequest, evaluate
from payer_B.rules import load as load_rules
from payer_B.store import load as load_repository

DATA = Path(__file__).parent / "data"
repository = load_repository(DATA / "fhir-repository.json")
rules = load_rules(DATA / "rules.json")

app = FastAPI(title="Payer B Backend System")


class CDSRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    hook: str | None = None
    hookInstance: str | None = None
    context: dict
    prefetch: dict | None = None


@app.post("/cds-services/{service_id}")
async def handle_payer_service(service_id: str, body: CDSRequest):
    try:
        return evaluate(service_id, body.model_dump(), repository, rules)
    except MalformedRequest as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

import logging
from contextlib import asynccontextmanager
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from payer_B.engine import MalformedRequest, evaluate
from payer_B.rules import load as load_rules
from payer_B.store import load as load_repository

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
DATA = Path(__file__).parent / "data"
repository = load_repository(DATA / "fhir-repository.json")
rules = load_rules(DATA / "rules.json")

QUESTIONNAIRE_DATA_PATH = DATA / "questionnaire.json"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Payer B ready patients=%s rules=%s", list(repository.patients), len(rules.rules))
    yield


app = FastAPI(title="Payer B Backend System", lifespan=lifespan)


class CDSRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    hook: str | None = None
    hookInstance: str | None = None
    context: dict
    prefetch: dict | None = None


@app.post("/cds-services/{service_id}")
async def handle_payer_service(service_id: str, body: CDSRequest):
    logger.info("Payer B request service_id=%s hook=%s", service_id, body.hook)
    try:
        result = evaluate(service_id, body.model_dump(), repository, rules)
        logger.info("Payer B response service_id=%s cards=%s", service_id, len(result.get("cards", [])))
        return result
    except MalformedRequest as error:
        logger.warning("Malformed CDS request service_id=%s detail=%s", service_id, error)
        raise HTTPException(status_code=400, detail=str(error)) from error


def load_questionnaire_bundle() -> dict:
    if not QUESTIONNAIRE_DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Payer questionnaire dataset not found.")
    return json.loads(QUESTIONNAIRE_DATA_PATH.read_text())

@app.post("/Questionnaire/$questionnaire-package")
async def handle_questionnaire_package(body: dict):
    logger.info("Payer B request: $questionnaire-package")
    bundle = load_questionnaire_bundle()
    return bundle

@app.post("/QuestionnaireResponse")
async def handle_questionnaire_response(body: dict):
    logger.info("Payer B submission: QuestionnaireResponse id=%s", body.get("id"))
    if body.get("resourceType") != "QuestionnaireResponse":
        raise HTTPException(status_code=400, detail="Invalid resourceType. Expected 'QuestionnaireResponse'.")
    if body.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Submitted QuestionnaireResponse status must be 'completed'.")
    
    resp_id = body.get("id", "qr-generated")
    repository.save_response(resp_id, body)
    
    return {
        "resourceType": "OperationOutcome",
        "issue": [{
            "severity": "information",
            "code": "informational",
            "diagnostics": f"QuestionnaireResponse {resp_id} successfully received and processed by Payer B."
        }]
    }
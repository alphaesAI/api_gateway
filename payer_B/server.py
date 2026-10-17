import logging
from contextlib import asynccontextmanager
from pathlib import Path

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

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Payer A ready")
    yield


app = FastAPI(title="Payer A Backend System", lifespan=lifespan)

@app.post("/cds-services/{service_id}")
async def handle_payer_service(service_id: str, request: Request):
    body = await request.json()
    logger.info("Payer A request service_id=%s hook=%s", service_id, body.get("hook"))
    
    # Payer A can look up rules dynamically for whatever service_id the Gateway forwards
    return {
        "cards": [
            {
                "summary": f"Payer A: Evaluated {service_id}",
                "detail": "Backend rules executed successfully.",
                "indicator": "info",
                "source": {"label": "Payer A Engine"}
            }
        ]
    }
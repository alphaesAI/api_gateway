import httpx
import logging
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cds-services", tags=["CDS Services Gateway"])

PAYER_BASE_URL = os.getenv("PAYER_BASE_URL")
logger.info("PAYER_BASE_URL=%s", PAYER_BASE_URL)

@router.get("")
async def get_cds_services():
    """GET /cds-services"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PAYER_BASE_URL}/cds-services", timeout=10.0)
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError as e:
            logger.error("Payer discovery unreachable error=%s", e)
            raise HTTPException(status_code=502, detail=f"Payer backend unreachable: {str(e)}")

@router.post("/{hook_id}")
async def post_cds_service(hook_id: str, request: Request):
    """POST /cds-services/{hook_id}"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{PAYER_BASE_URL}/cds-services/{hook_id}", json=body, timeout=15.0)
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError as e:
            logger.error("Payer communication error hook_id=%s error=%s", hook_id, e)
            raise HTTPException(status_code=502, detail=f"Payer backend communication error: {str(e)}")
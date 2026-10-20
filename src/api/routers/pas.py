import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.pas_services.connector import PASConnector
from src.pas_services.models.pas import PASSubmitRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fhir", tags=["Da Vinci PAS"])


@router.post("/Claim/$submit", status_code=status.HTTP_200_OK)
async def submit_prior_authorization(payload: PASSubmitRequest):
    """
    Handle Da Vinci PAS $submit requests and proxy to the payer backend engine.
    """
    logger.info("PAS request: Claim/$submit")
    try:
        response_data = await PASConnector.submit_prior_auth(payload)
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
    except Exception as error:
        logger.error("Error processing prior authorization submission: %s", error)
        raise HTTPException(status_code=500, detail=str(error)) from error
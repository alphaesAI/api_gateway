import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.dtr_services.connector import DTRConnector
from src.dtr_services.models.dtr import DTRQuestionnaireRequest, DTRQuestionnaireResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fhir", tags=["Da Vinci DTR"])


@router.post("/Questionnaire/$questionnaire-package")
async def get_questionnaire_package(payload: DTRQuestionnaireRequest):
    """
    Handle Da Vinci DTR $questionnaire-package requests and proxy to the payer backend engine.
    """
    logger.info("DTR request: $questionnaire-package")
    try:
        response_data = await DTRConnector.get_questionnaire_package(payload)
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
    except Exception as error:
        logger.error("Error fetching questionnaire package: %s", error)
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post("/QuestionnaireResponse", status_code=status.HTTP_201_CREATED)
async def submit_questionnaire_response(response_payload: DTRQuestionnaireResponse):
    """
    Handle Da Vinci DTR QuestionnaireResponse submission and proxy to the payer backend engine.
    """
    logger.info("DTR submission: QuestionnaireResponse")
    try:
        response_data = await DTRConnector.submit_questionnaire_response(response_payload)
        return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)
    except Exception as error:
        logger.warning("Error submitting questionnaire response: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error
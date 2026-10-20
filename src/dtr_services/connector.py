import logging
import httpx
from typing import Any
import os
from dotenv import load_dotenv
load_dotenv()

from src.dtr_services.models.dtr import DTRQuestionnaireRequest, DTRQuestionnaireResponse

logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")


class DTRConnector:
    @staticmethod
    async def get_questionnaire_package(payload: DTRQuestionnaireRequest) -> dict[str, Any]:
        logger.info("DTRConnector: Proxying $questionnaire-package to Payer B")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/Questionnaire/$questionnaire-package",
                json=payload.model_dump()
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def submit_questionnaire_response(payload: DTRQuestionnaireResponse) -> dict[str, Any]:
        logger.info("DTRConnector: Proxying QuestionnaireResponse submission to Payer B")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/QuestionnaireResponse",
                json=payload.model_dump()
            )
            response.raise_for_status()
            return response.json()
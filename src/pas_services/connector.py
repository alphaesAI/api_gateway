import logging
import httpx
from typing import Any
from src.pas_services.models.pas import PASSubmitRequest
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")


class PASConnector:
    @staticmethod
    async def submit_prior_auth(payload: PASSubmitRequest) -> dict[str, Any]:
        logger.info("PASConnector: Proxying Claim/$submit to Payer B")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/Claim/$submit",
                json=payload.model_dump()
            )
            response.raise_for_status()
            return response.json()
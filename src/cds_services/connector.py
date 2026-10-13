from fastapi import HTTPException
import httpx
import logging
from src.api import application

logger = logging.getLogger(__name__)

class DecisionEngineConnector:
    @staticmethod
    async def submit_for_decision(hook_id: str, cds_request: dict) -> dict:
        """
        Proxies the CDS Hooks decision request to the configured Payer backend URL.
        """
        logger.info(f"Received hookId for decision: {hook_id}")

        # Fetch services from global application configuration
        app_instance = application.get()
        if not app_instance or not hasattr(app_instance, "config"):
            raise HTTPException(status_code=500, detail="Application configuration not initialized.")

        services = app_instance.config.get("cds_services", [])
        service = next((s for s in services if s.get("id") == hook_id), None)

        if not service:
            raise HTTPException(status_code=404, detail=f"Cannot find a CDS service with the name: {hook_id}")

        backend_url = service.get("backend_url")

        # If no backend_url is configured, fallback to local mock/rule evaluation
        if not backend_url:
            logger.warning(f"No backend_url found for service {hook_id}. Returning default mock response.")
            return {"cards": [{"summary": "Local Evaluation", "detail": "No external payer backend configured."}]}

        # Forward the request to the Payer's actual server via asynchronous HTTP proxy
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(backend_url, json=cds_request, timeout=15.0)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Failed to connect to payer backend at {backend_url}: {str(e)}")
                raise HTTPException(status_code=502, detail=f"Payer backend unreachable: {str(e)}")
            except httpx.HTTPStatusError as e:
                logger.error(f"Payer backend returned error status: {e.response.status_code}")
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @staticmethod
    async def submit_feedback(hook_id: str, cds_feedback: dict) -> None:
        """
        Proxies the CDS Hooks feedback request to the configured Payer backend URL if available.
        """
        logger.info(f"Received feedback for hookId: {hook_id}")

        app_instance = application.get()
        if not app_instance or not hasattr(app_instance, "config"):
            raise HTTPException(status_code=500, detail="Application configuration not initialized.")

        services = app_instance.config.get("cds_services", [])
        service = next((s for s in services if s.get("id") == hook_id), None)

        if not service:
            raise HTTPException(status_code=404, detail=f"Cannot find a CDS service with the name: {hook_id}")

        backend_url = service.get("backend_url")

        if not backend_url:
            # Local fallback for feedback
            return

        # Forward feedback to the Payer backend
        feedback_url = f"{backend_url.rstrip('/')}/feedback"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(feedback_url, json=cds_feedback, timeout=10.0)
                response.raise_for_status()
            except httpx.RequestError as e:
                logger.error(f"Failed to submit feedback to payer backend at {feedback_url}: {str(e)}")
                # Feedback failure shouldn't necessarily block the client, but you can raise if needed
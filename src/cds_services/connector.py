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
        logger.info("Decision request hook_id=%s", hook_id)

        app_instance = application.get()
        if not app_instance or not hasattr(app_instance, "config"):
            logger.error("Application configuration is not initialized")
            raise HTTPException(status_code=500, detail="Application configuration not initialized.")

        services = app_instance.config.get("cds_services", [])
        service = next((s for s in services if s.get("id") == hook_id), None)

        if not service:
            logger.warning("No configured service for hook_id=%s", hook_id)
            raise HTTPException(status_code=404, detail=f"Cannot find a CDS service with the name: {hook_id}")

        backend_url = service.get("backend_url")

        if not backend_url:
            logger.warning("No backend_url for hook_id=%s. Returning local fallback.", hook_id)
            return {"cards": [{"summary": "Local Evaluation", "detail": "No external payer backend configured."}]}

        logger.info("Forwarding hook_id=%s to %s", hook_id, backend_url)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(backend_url, json=cds_request, timeout=15.0)
                response.raise_for_status()
                payload = response.json()
                logger.info("Payer response hook_id=%s status=%s cards=%s", hook_id, response.status_code, len(payload.get("cards", [])))
                return payload
            except httpx.RequestError as e:
                logger.error("Payer backend unreachable url=%s error=%s", backend_url, e)
                raise HTTPException(status_code=502, detail=f"Payer backend unreachable: {str(e)}")
            except httpx.HTTPStatusError as e:
                logger.error("Payer backend error url=%s status=%s", backend_url, e.response.status_code)
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    @staticmethod
    async def submit_feedback(hook_id: str, cds_feedback: dict) -> None:
        """
        Proxies the CDS Hooks feedback request to the configured Payer backend URL if available.
        """
        logger.info("Feedback request hook_id=%s", hook_id)

        app_instance = application.get()
        if not app_instance or not hasattr(app_instance, "config"):
            logger.error("Application configuration is not initialized")
            raise HTTPException(status_code=500, detail="Application configuration not initialized.")

        services = app_instance.config.get("cds_services", [])
        service = next((s for s in services if s.get("id") == hook_id), None)

        if not service:
            logger.warning("No configured service for feedback hook_id=%s", hook_id)
            raise HTTPException(status_code=404, detail=f"Cannot find a CDS service with the name: {hook_id}")

        backend_url = service.get("backend_url")

        if not backend_url:
            logger.warning("No backend_url for feedback hook_id=%s", hook_id)
            return

        feedback_url = f"{backend_url.rstrip('/')}/feedback"
        logger.info("Forwarding feedback hook_id=%s to %s", hook_id, feedback_url)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(feedback_url, json=cds_feedback, timeout=10.0)
                response.raise_for_status()
                logger.info("Feedback accepted hook_id=%s status=%s", hook_id, response.status_code)
            except httpx.RequestError as e:
                logger.error("Feedback unreachable url=%s error=%s", feedback_url, e)
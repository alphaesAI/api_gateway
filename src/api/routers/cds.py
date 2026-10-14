from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.api import application
from src.cds_services.models.cds import CDSRequest, CDSFeedback
from src.cds_services.connector import DecisionEngineConnector

router = APIRouter(prefix="/cds-services", tags=["cds services"])

@router.get("")
def get_cds_services():
    """
    List available CDS services.
    """
    app_instance = application.get()
    config = app_instance.config if app_instance else {}
    return {"services": config.get("cds_services", [])}

@router.post("/{hook_id}")
async def post_cds_service(hook_id: str, cds_request: CDSRequest):
    """
    Handle incoming CDS hook execution requests and proxy to payer backend.
    """
    app_instance = application.get()
    config = app_instance.config if app_instance else {}
    services = config.get("cds_services", [])
    service = next((s for s in services if s.get("id") == hook_id), None)

    if not service:
        raise HTTPException(status_code=404, detail=f"can not find a cds service with the name: {hook_id}")

    if cds_request.hook != service.get("hook"):
        raise HTTPException(
            status_code=400,
            detail=f"CDS service {hook_id} is not compatible with the hook {cds_request.hook}"
        )

    response_data = await DecisionEngineConnector.submit_for_decision(hook_id, cds_request.dict())
    return JSONResponse(content=response_data)

@router.post("/{hook_id}/feedback")
async def post_cds_feedback(hook_id: str, cds_feedback: CDSFeedback):
    """
    Handle CDS feedback submission.
    """
    app_instance = application.get()
    config = app_instance.config if app_instance else {}
    services = config.get("cds_services", [])
    service = next((s for s in services if s.get("id") == hook_id), None)

    if not service:
        raise HTTPException(status_code=404, detail=f"can not find a cds service with the name: {hook_id}")

    await DecisionEngineConnector.submit_feedback(hook_id, cds_feedback.dict())
    return JSONResponse(content={"message": "Feedback submitted successfully"})
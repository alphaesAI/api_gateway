from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="Payer A Backend System")

# 1. Payer Discovery Endpoint (Required by CDS Hooks spec)
@app.get("/cds-services")
def discover_services():
    """
    Returns the list of services supported by Payer A.
    When the Gateway or EHR queries this, Payer A publishes its catalog.
    """
    return {
        "services": [
            {
                "id": "crd-mri-spine-order-sign",
                "hook": "order-sign",
                "title": "CRD MRI Spine Order Sign",
                "description": "Evaluates coverage requirements and prior authorization for MRI Spine."
            }
        ]
    }

# 2. Payer Execution Endpoint for Specific Service
@app.post("/cds-services/crd-mri-spine-order-sign")
async def evaluate_mri_order(request: Request):
    body = await request.json()
    print("[Payer A Server] Evaluating incoming clinical order context...")
    
    # Real-world logic would parse FHIR resources from request['context'] or request['prefetch'] here
    
    return {
        "cards": [
            {
                "summary": "Payer A: Prior Authorization Required",
                "detail": "Coverage rules require documentation of 6 weeks of physical therapy before MRI approval.",
                "indicator": "warning",
                "source": {"label": "Payer A Clinical Rules Engine"}
            }
        ]
    }
from fastapi import FastAPI

from src.cds_services.models.cds import CDSRequest

app = FastAPI(title="Payer B Backend System")


@app.get("/cds-services")
def discover_services():
    """
    Returns the list of services supported by Payer B.
    When the Gateway or EHR queries this, Payer B publishes its catalog.
    """
    return {
        "services": [
            {
                "id": "prescribe-medication",
                "hook": "order-sign",
                "title": "Prescribe Medication",
                "description": "Evaluate coverage requirements for medication prescription",
            }
        ]
    }


@app.post("/cds-services/prescribe-medication")
async def handle_payer_b(cds_request: CDSRequest):
    """
    Handles the medication prescription request from the Gateway or EHR.
    This is where Payer B applies its formulary rules to determine coverage.
    """
    print(
        f"[Payer B Server] Processed Medication request (hook={cds_request.hook}) "
        "using Payer B formulary rules."
    )
    return {
        "cards": [
            {
                "summary": "Payer B: Preferred Drug Approved",
                "detail": "Under Payer B formulary, this medication is Tier 1 and fully covered.",
                "indicator": "info",
                "source": {"label": "Payer B Pharmacy Engine"}
            }
        ]
    }
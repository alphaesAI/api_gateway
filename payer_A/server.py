from fastapi import FastAPI, Request

app = FastAPI(title="Payer A Backend System")

@app.post("/cds-services/{service_id}")
async def handle_payer_service(service_id: str, request: Request):
    body = await request.json()
    print(f"[Payer A Server] Processing request for service ID: {service_id}")
    
    # Payer A can look up rules dynamically for whatever service_id the Gateway forwards
    return {
        "cards": [
            {
                "summary": f"Payer A: Evaluated {service_id}",
                "detail": "Backend rules executed successfully.",
                "indicator": "info",
                "source": {"label": "Payer A Engine"}
            }
        ]
    }
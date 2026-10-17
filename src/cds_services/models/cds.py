from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CDSServiceDefinition(BaseModel):
    id: str
    hook: str
    title: str
    description: str

class CDSRequest(BaseModel):
    hook: str
    hookInstance: str
    context: Dict[str, Any]
    prefetch: Optional[Dict[str, Any]] = None

    model_config = {
    "json_schema_extra": {
        "example": {
            "hook": "order-sign",
            "hookInstance": "6c171633-76b7-4e7e-b25a-f81b17b3cec0",
            "context": {
                "patientId": "Patient/1001",
                "draftOrders": {
                    "resourceType": "Bundle",
                    "type": "collection",
                    "entry": [
                        {
                            "resource": {
                                "resourceType": "ServiceRequest",
                                "status": "draft",
                                "intent": "order",
                                "subject": {"reference": "Patient/1001"},
                                "code": {
                                    "coding": [
                                        {
                                            "system": "http://www.ama-assn.org/go/cpt",
                                            "code": "72148"
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
}

class CDSFeedback(BaseModel):
    hookInstance: str
    outcome: Optional[str] = None
    acceptedSuggestions: Optional[List[str]] = None
    feedback: Optional[Dict[str, Any]] = None
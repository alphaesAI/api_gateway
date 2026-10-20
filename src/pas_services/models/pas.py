from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class PASSubmitRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "resourceType": "Parameters",
                "id": "PASSubmitInputExample",
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/davinci-pas/StructureDefinition/profile-parameters-in"
                    ]
                },
                "parameter": [
                    {
                        "name": "claim",
                        "resource": {
                            "resourceType": "Claim",
                            "id": "claim-lumbar-mri",
                            "status": "active",
                            "use": "preauthorization",
                            "patient": {"reference": "Patient/1001"},
                            "insurer": {"reference": "Organization/payer-b"}
                        }
                    }
                ]
            }
        }
    )

    resourceType: str = "Parameters"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    parameter: List[Dict[str, Any]]


class PASSubmitResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    resourceType: str
    id: Optional[str] = None
    outcome: Optional[str] = None
    disposition: Optional[str] = None
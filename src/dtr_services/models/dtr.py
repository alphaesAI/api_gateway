from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any


class DTRQuestionnaireRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "resourceType": "Parameters",
                "id": "QuestionnairePackageInputParamsExample",
                "meta": {
                    "profile": [
                        "http://hl7.org/fhir/us/davinci-dtr/StructureDefinition/dtr-qpackage-input-parameters"
                    ]
                },
                "parameter": [
                    {
                        "name": "coverage",
                        "resource": {
                            "resourceType": "Coverage",
                            "id": "cov-1001",
                            "status": "active",
                            "payor": [{"reference": "Organization/payer-b"}],
                            "beneficiary": {
                                "reference": "Patient/1001",
                                "display": "Ava Nguyen",
                            },
                            "subscriberId": "SUB-1001",
                        },
                    },
                    {
                        "name": "order",
                        "resource": {
                            "resourceType": "ServiceRequest",
                            "id": "sr-lumbar-mri",
                            "status": "active",
                            "intent": "order",
                            "code": {
                                "coding": [
                                    {
                                        "system": "http://snomed.info/sct",
                                        "code": "306442007",
                                        "display": "Magnetic resonance imaging of lumbar spine",
                                    }
                                ]
                            },
                            "subject": {
                                "reference": "Patient/1001",
                                "display": "Ava Nguyen",
                            },
                        },
                    },
                ],
            }
        },
    )

    resourceType: str = "Parameters"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    parameter: List[Dict[str, Any]]

class DTRQuestionnaireResponse(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "resourceType": "QuestionnaireResponse",
                "id": "qr-1001-72148",
                "status": "completed",
                "questionnaire": "http://payerb.org/fhir/Questionnaire/lumbar-mri-master",
                "subject": {
                    "reference": "Patient/1001",
                    "display": "Ava Nguyen"
                },
                "authored": "2026-10-18T17:14:00Z",
                "item": [
                    {
                        "linkId": "conservative_therapy_group",
                        "text": "Conservative Therapy Evaluation",
                        "item": [
                            {
                                "linkId": "had_conservative_therapy",
                                "text": "Has the patient completed at least 6 weeks of conservative therapy?",
                                "answer": [
                                    {
                                        "valueBoolean": True
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    )

    resourceType: str = "QuestionnaireResponse"
    id: Optional[str] = None
    status: str
    questionnaire: str
    subject: Dict[str, Any]
    authored: Optional[str] = None
    item: List[Dict[str, Any]]
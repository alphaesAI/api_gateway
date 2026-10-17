import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, patients: dict[str, dict], coverages: dict[str, list[dict]], payer_name: str):
        self.patients = patients
        self.coverages = coverages
        self.payer_name = payer_name

    def patient(self, patient_id: str) -> dict | None:
        found = self.patients.get(patient_id)
        logger.info("Patient lookup id=%s found=%s", patient_id, found is not None)
        return found

    def coverages_for(self, patient_id: str) -> list[dict]:
        found = self.coverages.get(patient_id, [])
        logger.info("Coverage lookup patient_id=%s count=%s", patient_id, len(found))
        return found


def load(path: Path) -> Repository:
    logger.info("Loading FHIR repository %s", path)
    bundle = json.loads(path.read_text())
    if bundle.get("resourceType") != "Bundle":
        logger.error("File is not a FHIR Bundle: %s", path)
        raise ValueError(f"{path} is not a FHIR Bundle")

    patients: dict[str, dict] = {}
    coverages: dict[str, list[dict]] = {}
    payer_name = "Payer"

    for entry in bundle.get("entry", []):
        resource = entry.get("resource") or {}
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        if resource_type == "Organization" and resource.get("name"):
            payer_name = resource["name"]
        elif resource_type == "Patient" and resource_id:
            patients[resource_id] = resource
        elif resource_type == "Coverage" and resource_id:
            patient_id = _patient_id(resource.get("beneficiary", {}).get("reference"))
            if patient_id:
                coverages.setdefault(patient_id, []).append(resource)

    logger.info("FHIR repository loaded payer=%s patients=%s", payer_name, list(patients))
    return Repository(patients, coverages, payer_name)


def _patient_id(reference: str | None) -> str | None:
    if not reference:
        return None
    if reference.startswith("Patient/"):
        return reference.split("/", 1)[1]
    return reference

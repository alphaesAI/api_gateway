import logging
from urllib.parse import urlencode

from payer_B.rules import Rule, RuleSet
from payer_B.store import Repository

logger = logging.getLogger(__name__)
ORDER_TYPES = {"ServiceRequest", "MedicationRequest", "DeviceRequest"}


class MalformedRequest(ValueError):
    pass


def evaluate(service_id: str, request: dict, repository: Repository, rules: RuleSet) -> dict:
    logger.info("Evaluate service_id=%s hook=%s", service_id, request.get("hook"))
    patient_id = _patient_id(request)
    orders = _draft_orders(request)
    patient = repository.patient(patient_id)
    coverages = repository.coverages_for(patient_id)
    logger.info("Lookup patient_id=%s found=%s coverages=%s", patient_id, patient is not None, len(coverages))

    if patient is None or not coverages:
        logger.info("Member not on file patient_id=%s", patient_id)
        return _cards([_card(
            summary="Member not found",
            detail=f"No Patient and Coverage on file for {patient_id}.",
            indicator="critical",
            source=repository.payer_name,
        )])

    active = next((item for item in coverages if item.get("status") == "active"), None)
    if active is None:
        statuses = ", ".join(f"{item.get('id')}={item.get('status')}" for item in coverages)
        logger.info("Coverage not active patient_id=%s statuses=%s", patient_id, statuses)
        return _cards([_card(
            summary="Coverage is not active",
            detail=f"Coverage status is not active ({statuses}).",
            indicator="critical",
            source=repository.payer_name,
        )])

    logger.info("Active coverage id=%s orders=%s", active.get("id"), len(orders))
    cards = []
    for order in orders:
        for coding in _codings(order):
            system = coding.get("system", "")
            code = coding.get("code", "")
            rule = rules.match(system, code)
            if rule is None:
                logger.info("No rule for %s|%s", system, code)
                continue
            logger.info("Rule matched %s|%s require_pa=%s", system, code, rule.require_pa)
            cards.append(_rule_card(service_id, patient_id, rule, rules.smart_launch_url, repository.payer_name))

    if not cards:
        logger.info("No submitted code matched a payer rule")
        cards.append(_card(
            summary="No payer rule applied",
            detail="Coverage is active. None of the submitted codes matched a payer rule.",
            indicator="info",
            source=repository.payer_name,
        ))
    indicators = [card["indicator"] for card in cards]
    logger.info("Evaluation result cards=%s indicators=%s", len(cards), indicators)
    return _cards(cards)


def _patient_id(request: dict) -> str:
    context = request.get("context") or {}
    raw = context.get("patientId")
    if not raw:
        prefetch = request.get("prefetch") or {}
        patient = prefetch.get("patient")
        if isinstance(patient, dict):
            raw = patient.get("id")
        elif isinstance(patient, str):
            raw = patient
    if not isinstance(raw, str) or not raw.strip():
        logger.warning("Patient id missing from context and prefetch")
        raise MalformedRequest("patient id is missing from context.patientId and prefetch.patient")
    if raw.startswith("Patient/"):
        raw = raw.split("/", 1)[1]
    logger.info("Extracted patient_id=%s", raw)
    return raw


def _draft_orders(request: dict) -> list[dict]:
    draft = (request.get("context") or {}).get("draftOrders")
    if draft is None:
        logger.warning("context.draftOrders is missing")
        raise MalformedRequest("context.draftOrders is missing")

    resources: list[dict] = []
    if isinstance(draft, dict) and draft.get("resourceType") == "Bundle":
        for entry in draft.get("entry") or []:
            resource = entry.get("resource") if isinstance(entry, dict) else None
            if not isinstance(resource, dict) or not resource.get("resourceType"):
                logger.warning("Draft order entry is missing resourceType")
                raise MalformedRequest("draft order entry is missing resourceType")
            if resource["resourceType"] in ORDER_TYPES:
                resources.append(resource)
    elif isinstance(draft, dict):
        if not draft.get("resourceType"):
            logger.warning("Draft order is missing resourceType")
            raise MalformedRequest("draft order is missing resourceType")
        if draft["resourceType"] in ORDER_TYPES:
            resources.append(draft)
    else:
        logger.warning("context.draftOrders is not a FHIR resource or Bundle")
        raise MalformedRequest("context.draftOrders must be a FHIR resource or Bundle")

    if not resources:
        logger.warning("Draft orders contained no ServiceRequest, MedicationRequest, or DeviceRequest")
        raise MalformedRequest("context.draftOrders has no ServiceRequest, MedicationRequest, or DeviceRequest")
    logger.info("Extracted draft orders=%s types=%s", len(resources), [item.get("resourceType") for item in resources])
    return resources


def _codings(resource: dict) -> list[dict]:
    code = resource.get("code") or {}
    # MedicationRequest uses medicationCodeableConcept.
    if resource.get("resourceType") == "MedicationRequest":
        code = resource.get("medicationCodeableConcept") or code
    codings = code.get("coding") if isinstance(code, dict) else None
    if not isinstance(codings, list):
        return []
    return [item for item in codings if isinstance(item, dict)]


def _rule_card(service_id: str, patient_id: str, rule: Rule, smart_launch_url: str, source: str) -> dict:
    label = rule.display or rule.code
    logger.info("Building card code=%s require_pa=%s", rule.code, rule.require_pa)
    if rule.require_pa:
        detail = rule.document_needed or f"Prior authorization is required for {label}."
        query = urlencode({
            "service": service_id,
            "patient": patient_id,
            "system": rule.system,
            "code": rule.code,
        })
        return _card(
            summary=f"Prior authorization required for {label}",
            detail=detail,
            indicator="warning",
            source=source,
            links=[{
                "label": "Launch SMART app",
                "url": f"{smart_launch_url}?{query}",
                "type": "smart",
            }],
        )
    return _card(
        summary=f"No prior authorization required for {label}",
        detail=f"Coverage is active for {label} ({rule.system}|{rule.code}).",
        indicator="info",
        source=source,
    )


def _card(summary: str, detail: str, indicator: str, source: str, links: list | None = None) -> dict:
    card = {
        "summary": summary,
        "detail": detail,
        "indicator": indicator,
        "source": {"label": source},
    }
    if links:
        card["links"] = links
    return card


def _cards(cards: list[dict]) -> dict:
    return {"cards": cards}

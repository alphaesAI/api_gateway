import json
from pathlib import Path


class Rule:
    def __init__(self, system: str, code: str, display: str | None, require_pa: bool, document_needed: str | None):
        self.system = system
        self.code = code
        self.display = display
        self.require_pa = require_pa
        self.document_needed = document_needed


class RuleSet:
    def __init__(self, smart_launch_url: str, rules: dict[tuple[str, str], Rule]):
        self.smart_launch_url = smart_launch_url
        self.rules = rules

    def match(self, system: str, code: str) -> Rule | None:
        return self.rules.get((system, code))


def load(path: Path) -> RuleSet:
    payload = json.loads(path.read_text())
    smart_launch_url = payload.get("smartLaunchUrl")
    if not smart_launch_url:
        raise ValueError(f"{path} is missing smartLaunchUrl")

    rules: dict[tuple[str, str], Rule] = {}
    for item in payload.get("rules", []):
        system = item.get("system")
        code = item.get("code")
        if not system or not code or "require_pa" not in item:
            raise ValueError(f"Rule is missing system, code, or require_pa: {item}")
        rules[(system, code)] = Rule(
            system=system,
            code=code,
            display=item.get("display"),
            require_pa=bool(item["require_pa"]),
            document_needed=item.get("document_needed"),
        )
    return RuleSet(smart_launch_url, rules)

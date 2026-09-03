from __future__ import annotations

from pathlib import Path

import yaml


class ProfileError(ValueError):
    pass


REQUIRED_TOP_LEVEL = {
    "specm_version",
    "profile",
    "required_capabilities",
    "state_domains",
    "normative_invariants",
    "backend_claims",
    "forbidden_claims_without_evidence",
}


def load_profile(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProfileError("profile must be a mapping")

    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    if missing:
        raise ProfileError(f"missing required profile sections: {', '.join(missing)}")

    profile = data.get("profile")
    if not isinstance(profile, dict) or not profile.get("id") or not profile.get("name"):
        raise ProfileError("profile.id and profile.name are required")

    required = data.get("required_capabilities")
    if not isinstance(required, list) or not required:
        raise ProfileError("required_capabilities must be a non-empty list")
    if len(required) != len(set(required)):
        raise ProfileError("required_capabilities contains duplicates")
    if any(not isinstance(item, str) or not item for item in required):
        raise ProfileError("required_capabilities entries must be non-empty strings")

    optional = data.get("optional_capabilities", [])
    if not isinstance(optional, list) or any(not isinstance(item, str) or not item for item in optional):
        raise ProfileError("optional_capabilities must be a string list")
    if len(optional) != len(set(optional)):
        raise ProfileError("optional_capabilities contains duplicates")
    overlap = sorted(set(required) & set(optional))
    if overlap:
        raise ProfileError(f"capabilities cannot be both required and optional: {', '.join(overlap)}")

    invariants = data.get("normative_invariants")
    if not isinstance(invariants, list) or not invariants:
        raise ProfileError("normative_invariants must be a non-empty list")
    ids: list[str] = []
    for item in invariants:
        if not isinstance(item, dict) or not item.get("id") or not item.get("statement"):
            raise ProfileError("each invariant requires id and statement")
        ids.append(str(item["id"]))
    if len(ids) != len(set(ids)):
        raise ProfileError("normative invariant IDs must be unique")

    domains = data.get("state_domains")
    if not isinstance(domains, dict) or not domains:
        raise ProfileError("state_domains must be a non-empty mapping")

    return data


def profile_summary(data: dict[str, object]) -> dict[str, object]:
    profile = data["profile"]
    assert isinstance(profile, dict)
    invariants = data["normative_invariants"]
    assert isinstance(invariants, list)
    domains = data["state_domains"]
    assert isinstance(domains, dict)
    required = data["required_capabilities"]
    assert isinstance(required, list)
    optional = data.get("optional_capabilities", [])
    assert isinstance(optional, list)

    return {
        "valid": True,
        "profile_id": profile["id"],
        "name": profile["name"],
        "status": profile.get("status", "UNKNOWN"),
        "required_capability_count": len(required),
        "optional_capability_count": len(optional),
        "state_domains": sorted(domains),
        "normative_invariant_count": len(invariants),
    }

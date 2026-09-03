from __future__ import annotations

from pathlib import Path
import yaml

from .models import ConformanceLevel
from .profile import load_profile
from .registry import transitions


class BackendError(ValueError):
    pass


LEVELS = tuple(level.value for level in ConformanceLevel)
REQUIRED_EVIDENCE = {
    "C0_SPECIFIED": (),
    "C1_MODEL": ("model",),
    "C2_UNIT": ("unit",),
    "C3_ARCH": ("architecture", "negative"),
    "C4_PLATFORM": ("platform",),
    "C5_KERNEL": ("kernel",),
    "C6_WORKLOAD": ("workload",),
    "C7_HARDWARE": ("hardware",),
}


def load_backend(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise BackendError("backend manifest must be a mapping")
    required = {"specm_version", "backend", "profiles", "capabilities", "implemented_transitions", "claim", "evidence", "limitations"}
    missing = sorted(required - raw.keys())
    if missing:
        raise BackendError(f"missing backend sections: {', '.join(missing)}")
    backend = raw["backend"]
    if not isinstance(backend, dict) or not all(backend.get(x) for x in ("id", "architecture", "platform")):
        raise BackendError("backend id, architecture, and platform are required")
    for key in ("profiles", "capabilities", "implemented_transitions", "evidence", "limitations"):
        if not isinstance(raw[key], list):
            raise BackendError(f"{key} must be a list")
    if len(raw["capabilities"]) != len(set(raw["capabilities"])):
        raise BackendError("capabilities contains duplicates")
    known = {item.id for item in transitions()}
    unknown = sorted(set(raw["implemented_transitions"]) - known)
    if unknown:
        raise BackendError(f"unknown implemented transitions: {', '.join(unknown)}")
    claim = raw["claim"]
    if not isinstance(claim, dict) or claim.get("level") not in LEVELS or not claim.get("profile"):
        raise BackendError("claim requires a known level and profile")
    if claim["profile"] not in raw["profiles"]:
        raise BackendError("claimed profile is not listed as supported")
    evidence = raw["evidence"]
    categories = set()
    for item in evidence:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k] for k in ("id", "category", "artifact", "result")):
            raise BackendError("each evidence item requires id, category, artifact, and result")
        if item["result"] != "pass":
            raise BackendError(f"evidence {item['id']} does not record a pass")
        categories.add(item["category"])
    level_index = LEVELS.index(claim["level"])
    needed = {category for level in LEVELS[:level_index + 1] for category in REQUIRED_EVIDENCE[level]}
    absent = sorted(needed - categories)
    if absent:
        raise BackendError(f"claim {claim['level']} lacks evidence categories: {', '.join(absent)}")
    if claim["level"] == "C7_HARDWARE" and not backend.get("hardware_model"):
        raise BackendError("C7_HARDWARE requires backend.hardware_model")
    for profile_path in raw["profiles"]:
        profile = load_profile(path.parent / profile_path if not Path(profile_path).is_absolute() else Path(profile_path))
        unsupported = sorted(set(profile["required_capabilities"]) - set(raw["capabilities"]))
        if unsupported:
            raise BackendError(f"profile {profile['profile']['id']} requires unsupported capabilities: {', '.join(unsupported)}")
    return raw


def backend_summary(raw: dict[str, object]) -> dict[str, object]:
    backend = raw["backend"]
    claim = raw["claim"]
    return {"valid": True, "backend_id": backend["id"], "architecture": backend["architecture"],
            "platform": backend["platform"], "claim": claim, "evidence_count": len(raw["evidence"]),
            "implemented_transition_count": len(raw["implemented_transitions"])}

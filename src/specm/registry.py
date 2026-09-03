from __future__ import annotations

import json
from importlib.resources import files

from .models import Transition


class RegistryError(ValueError):
    pass


LIST_FIELDS = (
    "inputs", "outputs", "preconditions", "postconditions", "ordering",
    "privilege", "failures", "normative_invariants", "required_capabilities",
)


def validate_registry(raw: object) -> list[Transition]:
    if not isinstance(raw, list) or not raw:
        raise RegistryError("transition registry must be a non-empty list")
    result: list[Transition] = []
    ids: set[str] = set()
    names: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise RegistryError(f"transition {index} must be an object")
        for field in ("id", "name", "domain", "intent", *LIST_FIELDS):
            if field not in item:
                raise RegistryError(f"transition {index} missing required field: {field}")
        for field in ("id", "name", "domain", "intent"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise RegistryError(f"transition {index}.{field} must be a non-empty string")
        for field in LIST_FIELDS:
            value = item[field]
            if not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value):
                raise RegistryError(f"transition {item['id']}.{field} must be a string list")
        if item["id"] in ids:
            raise RegistryError(f"duplicate transition id: {item['id']}")
        if item["name"] in names:
            raise RegistryError(f"duplicate transition name: {item['name']}")
        ids.add(item["id"])
        names.add(item["name"])
        result.append(Transition(**{field: tuple(item[field]) if field in LIST_FIELDS else item[field]
                                    for field in ("id", "name", "domain", "intent", *LIST_FIELDS)}))
    return sorted(result, key=lambda item: item.id)


def transitions() -> list[Transition]:
    path = files("specm.data").joinpath("transitions.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return validate_registry(raw)


def registry_document() -> dict[str, object]:
    items = transitions()
    return {
        "count": len(items),
        "transitions": [item.to_dict() for item in items],
    }

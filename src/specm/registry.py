from __future__ import annotations

import json
from importlib.resources import files

from .models import Transition


def transitions() -> list[Transition]:
    path = files("specm.data").joinpath("transitions.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    result = [
        Transition(
            id=item["id"],
            name=item["name"],
            domain=item["domain"],
            intent=item["intent"],
            preconditions=tuple(item.get("preconditions", [])),
            postconditions=tuple(item.get("postconditions", [])),
            invariants=tuple(item.get("invariants", [])),
        )
        for item in raw
    ]
    return sorted(result, key=lambda item: item.id)


def registry_document() -> dict[str, object]:
    items = transitions()
    return {
        "count": len(items),
        "transitions": [item.to_dict() for item in items],
    }

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class ConformanceLevel(str, Enum):
    C0_SPECIFIED = "C0_SPECIFIED"
    C1_MODEL = "C1_MODEL"
    C2_UNIT = "C2_UNIT"
    C3_ARCH = "C3_ARCH"
    C4_PLATFORM = "C4_PLATFORM"
    C5_KERNEL = "C5_KERNEL"
    C6_WORKLOAD = "C6_WORKLOAD"
    C7_HARDWARE = "C7_HARDWARE"


@dataclass(frozen=True)
class Transition:
    id: str
    name: str
    domain: str
    intent: str
    preconditions: tuple[str, ...]
    postconditions: tuple[str, ...]
    invariants: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        for key in ("preconditions", "postconditions", "invariants"):
            value[key] = list(value[key])
        return value


@dataclass(frozen=True)
class ConformanceClaim:
    backend: str
    profile: str
    level: ConformanceLevel
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "profile": self.profile,
            "level": self.level.value,
            "evidence": list(self.evidence),
        }

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backend import BackendError, backend_summary, load_backend
from .model_backend import ModelMachine
from .profile import ProfileError, load_profile, profile_summary
from .registry import registry_document


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _model_smoke(cpu_count: int) -> dict[str, object]:
    machine = ModelMachine(cpu_count=cpu_count)
    machine.interrupt_disable()
    machine.address_space_activate(1)
    before = machine.time_now()
    generation = machine.translation_sync(1)
    machine.userspace_enter()
    after = machine.time_now()
    return {
        "valid": after >= before,
        "translation_generation": generation,
        "snapshot": machine.snapshot(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="specm",
        description="Inspect and exercise the Spec-M canonical machine model",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-profile")
    validate.add_argument("profile", type=Path)

    backend = sub.add_parser("validate-backend")
    backend.add_argument("manifest", type=Path)

    conformance = sub.add_parser("conformance")
    conformance.add_argument("manifest", type=Path)

    sub.add_parser("transitions")

    model = sub.add_parser("model-smoke")
    model.add_argument("--cpus", type=int, default=1)

    args = parser.parse_args(argv)

    try:
        if args.command == "validate-profile":
            _emit(profile_summary(load_profile(args.profile)))
        elif args.command in ("validate-backend", "conformance"):
            _emit(backend_summary(load_backend(args.manifest)))
        elif args.command == "transitions":
            _emit(registry_document())
        elif args.command == "model-smoke":
            _emit(_model_smoke(args.cpus))
        else:
            parser.error("unknown command")
    except (OSError, BackendError, ProfileError, ValueError, RuntimeError) as exc:
        _emit({"valid": False, "error": str(exc)})
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

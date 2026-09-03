from pathlib import Path
import copy
import pytest

from specm.backend import BackendError, load_backend


def test_seed_manifests_are_honest_c0_declarations() -> None:
    for path in (Path("backends/riscv64/qemu-virt/manifest.yaml"), Path("backends/x86_64/qemu-pc/manifest.yaml")):
        assert load_backend(path)["claim"]["level"] == "C0_SPECIFIED"


def test_architecture_claim_requires_evidence(tmp_path: Path) -> None:
    import yaml
    source = Path("backends/riscv64/qemu-virt/manifest.yaml")
    raw = copy.deepcopy(load_backend(source))
    raw["profiles"] = [str(Path("profiles/core.yaml").resolve())]
    raw["claim"] = {"profile": raw["profiles"][0], "level": "C3_ARCH"}
    target = tmp_path / "bad.yaml"
    target.write_text(yaml.safe_dump(raw))
    with pytest.raises(BackendError, match="architecture"):
        load_backend(target)


def test_hardware_claim_requires_named_hardware(tmp_path: Path) -> None:
    import yaml
    source = Path("backends/riscv64/qemu-virt/manifest.yaml")
    raw = copy.deepcopy(load_backend(source))
    raw["profiles"] = [str(Path("profiles/core.yaml").resolve())]
    raw["claim"] = {"profile": raw["profiles"][0], "level": "C7_HARDWARE"}
    raw["evidence"] = [{"id": c, "category": c, "artifact": f"evidence/{c}.json", "result": "pass"}
                       for c in ("model", "unit", "architecture", "negative", "platform", "kernel", "workload", "hardware")]
    target = tmp_path / "bad.yaml"
    target.write_text(yaml.safe_dump(raw))
    with pytest.raises(BackendError, match="hardware_model"):
        load_backend(target)

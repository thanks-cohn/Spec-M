import json

from specm.cli import main


def test_transitions_cli_is_json(capsys) -> None:
    assert main(["transitions"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] >= 1


def test_model_smoke_reports_valid(capsys) -> None:
    assert main(["model-smoke", "--cpus", "2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
    assert len(payload["snapshot"]["cpus"]) == 2


def test_validate_backend_cli_is_deterministic_json(capsys) -> None:
    path = "backends/riscv64/qemu-virt/manifest.yaml"
    assert main(["validate-backend", path]) == 0
    first = capsys.readouterr().out
    assert main(["validate-backend", path]) == 0
    assert capsys.readouterr().out == first
    assert json.loads(first)["claim"]["level"] == "C0_SPECIFIED"

from pathlib import Path

from specm.profile import load_profile, profile_summary


def test_core_profile_is_structurally_valid() -> None:
    data = load_profile(Path("profiles/core.yaml"))
    summary = profile_summary(data)
    assert summary["valid"] is True
    assert summary["profile_id"] == "specm-core"
    assert summary["normative_invariant_count"] >= 1

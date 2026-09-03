from specm.registry import transitions


def test_transition_ids_are_unique_and_sorted() -> None:
    items = transitions()
    ids = [item.id for item in items]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_seed_registry_covers_multiple_machine_domains() -> None:
    domains = {item.domain for item in transitions()}
    assert {"cpu", "memory", "time", "execution"}.issubset(domains)

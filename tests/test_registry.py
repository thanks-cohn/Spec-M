from specm.registry import transitions


def test_transition_ids_are_unique_and_sorted() -> None:
    items = transitions()
    ids = [item.id for item in items]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_seed_registry_covers_multiple_machine_domains() -> None:
    domains = {item.domain for item in transitions()}
    assert {"cpu", "memory", "time", "execution"}.issubset(domains)


def test_registry_rejects_duplicate_ids() -> None:
    import pytest
    from specm.registry import RegistryError, validate_registry
    item = transitions()[0].to_dict()
    with pytest.raises(RegistryError, match="duplicate transition id"):
        validate_registry([item, item])


def test_transition_contract_fields_are_explicit() -> None:
    for item in transitions():
        assert item.intent
        assert item.preconditions and item.postconditions
        assert item.ordering and item.privilege and item.failures

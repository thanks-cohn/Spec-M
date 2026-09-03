import pytest

from specm.model_backend import ModelMachine


def test_monotonic_time_never_moves_backward() -> None:
    machine = ModelMachine()
    values = [machine.time_now() for _ in range(5)]
    assert values == sorted(values)


def test_userspace_requires_active_address_space() -> None:
    machine = ModelMachine()
    with pytest.raises(RuntimeError):
        machine.userspace_enter()


def test_address_space_and_translation_state_are_explicit() -> None:
    machine = ModelMachine()
    machine.address_space_activate(7)
    assert machine.cpu().active_address_space == 7
    assert machine.translation_sync(7) == 1
    assert machine.translation_sync(7) == 2


def test_userspace_entry_reduces_privilege() -> None:
    machine = ModelMachine()
    machine.address_space_activate(1)
    machine.userspace_enter()
    assert machine.cpu().privilege == "user"

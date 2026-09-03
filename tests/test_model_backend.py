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


def test_permission_removal_requires_sync_and_then_takes_effect() -> None:
    from specm.model_backend import READ, WRITE
    machine = ModelMachine()
    machine.address_space_activate(1)
    machine.map(1, 0x1000, READ | WRITE)
    machine.translation_sync(1)
    assert machine.access(0x1000, WRITE)
    machine.map(1, 0x1000, READ)
    assert machine.access(0x1000, WRITE)  # deliberately stale before synchronization
    machine.translation_sync(1)
    assert not machine.access(0x1000, WRITE)


def test_user_cannot_access_kernel_only_mapping() -> None:
    from specm.model_backend import READ
    machine = ModelMachine()
    machine.address_space_activate(1)
    machine.map(1, 0x2000, READ)
    machine.translation_sync(1)
    machine.userspace_enter()
    assert not machine.access(0x2000, READ)


def test_clock_regression_is_rejected() -> None:
    machine = ModelMachine()
    machine.time_now()
    with pytest.raises(ValueError, match="regress"):
        machine.set_time_for_test(0)


def test_monotonic_clock_domain_is_shared_by_cpus() -> None:
    machine = ModelMachine(cpu_count=2)
    assert [machine.time_now(1), machine.time_now(0), machine.time_now(1)] == [0, 1, 2]


def test_deadline_and_cpu_signal_are_explicit() -> None:
    machine = ModelMachine(cpu_count=2)
    machine.timer_set_deadline(2)
    for _ in range(3):
        machine.time_now()
    assert machine.deadline_pending
    machine.cpu_signal(1, "reschedule")
    assert machine.cpu(1).pending_signals == ["reschedule"]

from __future__ import annotations

from dataclasses import dataclass, field


READ, WRITE, EXECUTE, USER = 1, 2, 4, 8


@dataclass
class ModelCpu:
    cpu_id: int
    interrupts_enabled: bool = False
    active_address_space: int | None = None
    privilege: str = "kernel"
    pending_signals: list[str] = field(default_factory=list)


@dataclass
class ModelMachine:
    """A deliberately tiny deterministic state model for Spec-M contract tests.

    This is not an emulator and not a hardware backend. It exists so semantic
    transitions can be tested before being tied to x86-64 or RV64 mechanisms.
    """

    cpu_count: int = 1
    cpus: dict[int, ModelCpu] = field(init=False)
    translation_generation: dict[int, int] = field(default_factory=dict)
    mappings: dict[int, dict[int, int]] = field(default_factory=dict)
    visible_mappings: dict[int, dict[int, int]] = field(default_factory=dict)
    deadline: int | None = None
    deadline_pending: bool = False
    clock_value: int = 0
    fences: list[str] = field(default_factory=list)
    boot_manifest: dict[str, object] = field(default_factory=lambda: {
        "memory_regions": [], "kernel_image": None, "command_line": "", "cpu_ids": [0]
    })

    def __post_init__(self) -> None:
        if self.cpu_count < 1:
            raise ValueError("cpu_count must be positive")
        self.cpus = {cpu_id: ModelCpu(cpu_id) for cpu_id in range(self.cpu_count)}
        self.boot_manifest["cpu_ids"] = list(range(self.cpu_count))

    def cpu(self, cpu_id: int = 0) -> ModelCpu:
        try:
            return self.cpus[cpu_id]
        except KeyError as exc:
            raise ValueError(f"unknown cpu {cpu_id}") from exc

    def interrupt_disable(self, cpu_id: int = 0) -> None:
        self.cpu(cpu_id).interrupts_enabled = False

    def interrupt_enable(self, cpu_id: int = 0) -> None:
        self.cpu(cpu_id).interrupts_enabled = True

    def address_space_activate(self, address_space: int, cpu_id: int = 0) -> None:
        if address_space < 0:
            raise ValueError("address-space id must be non-negative")
        self.cpu(cpu_id).active_address_space = address_space
        self.translation_generation.setdefault(address_space, 0)

    def translation_sync(self, address_space: int) -> int:
        if address_space not in self.translation_generation:
            raise ValueError("address space has not been activated")
        self.translation_generation[address_space] += 1
        self.visible_mappings[address_space] = dict(self.mappings.get(address_space, {}))
        return self.translation_generation[address_space]

    def time_now(self, cpu_id: int = 0) -> int:
        self.cpu(cpu_id)  # validate the caller's CPU identity
        value = self.clock_value
        self.clock_value += 1
        if self.deadline is not None and value >= self.deadline:
            self.deadline_pending = True
            self.deadline = None
        return value

    def set_time_for_test(self, value: int, cpu_id: int = 0) -> None:
        self.cpu(cpu_id)
        if value < self.clock_value:
            raise ValueError("monotonic clock cannot regress")
        self.clock_value = value

    def timer_set_deadline(self, deadline: int, cpu_id: int = 0) -> None:
        self.cpu(cpu_id)
        if deadline < self.clock_value:
            raise ValueError("deadline is in the past")
        self.deadline, self.deadline_pending = deadline, False

    def map(self, address_space: int, address: int, permissions: int) -> None:
        if address_space not in self.translation_generation:
            raise ValueError("address space has not been activated")
        self.mappings.setdefault(address_space, {})[address] = permissions

    def access(self, address: int, permission: int, cpu_id: int = 0) -> bool:
        cpu = self.cpu(cpu_id)
        if cpu.active_address_space is None:
            return False
        actual = self.visible_mappings.get(cpu.active_address_space, {}).get(address, 0)
        if cpu.privilege == "user" and not actual & USER:
            return False
        return actual & permission == permission

    def cpu_signal(self, target: int, signal: str) -> None:
        self.cpu(target).pending_signals.append(signal)

    def memory_fence(self, order: str) -> None:
        if order not in {"relaxed", "acquire", "release", "acquire_release", "sequentially_consistent"}:
            raise ValueError("unknown memory order")
        self.fences.append(order)

    def userspace_enter(self, cpu_id: int = 0) -> None:
        cpu = self.cpu(cpu_id)
        if cpu.active_address_space is None:
            raise RuntimeError("userspace entry requires an active address space")
        cpu.privilege = "user"

    def snapshot(self) -> dict[str, object]:
        return {
            "cpus": {
                str(cpu_id): {
                    "interrupts_enabled": cpu.interrupts_enabled,
                    "active_address_space": cpu.active_address_space,
                    "privilege": cpu.privilege,
                    "pending_signals": list(cpu.pending_signals),
                }
                for cpu_id, cpu in sorted(self.cpus.items())
            },
            "deadline": self.deadline,
            "deadline_pending": self.deadline_pending,
            "clock_value": self.clock_value,
            "fences": list(self.fences),
            "boot_manifest": self.boot_manifest,
            "translation_generation": {
                str(key): value for key, value in sorted(self.translation_generation.items())
            },
        }
